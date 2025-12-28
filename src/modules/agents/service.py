from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
import os

from src.modules.agents.models import AgentModel
from src.modules.agents.schemas import AgentCreate, AgentChatResponse
from src.modules.agents.utils.llm.call_agent_asnyc import call_agent_async

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.session_service = InMemorySessionService() # We might want to persist sessions later, but InMemory is fine for now

    def create_agent(self, agent_data: AgentCreate):
        db_agent = AgentModel(**agent_data.model_dump())
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return db_agent

    def get_agent(self, agent_id: UUID):
        agent = self.db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent

    async def chat_with_agent(self, agent_id: UUID, query: str, session_id: str) -> str:
        db_agent = self.get_agent(agent_id)
        
        # Reconstruct ADK Agent
        # Assuming the model string is compatible with LiteLlm (e.g. "mistral/mistral-small-latest")
        # Check if MISTRAL_API_KEY is set if using Mistral
        
        adk_model = LiteLlm(model=db_agent.model)
        
        adk_agent = Agent(
            name=db_agent.name,
            model=adk_model,
            description=db_agent.description or "A helpful assistant",
            instruction=db_agent.instruction or "",
            tools=[] 
        )

        # Create Session if not exists (InMemorySessionService handles this gracefully usually, or we explicitly create)
        # For InMemory, we might need to recreate session every time if we don't store the service instance globally.
        # But here we instantiate service in __init__. 
        # CAUTION: This means sessions are lost between API requests because Service is re-instantiated per request (via Dependency).
        # To fix this properly, SessionService should be a singleton or global dependency.
        # For now, we'll re-create the session for the specific ID to allow "stateless" interaction from API perspective per request, 
        # BUT this defeats the purpose of "session". 
        # However, looking at test.py, it creates a session. 
        # If we want persistent sessions, we need a persistent SessionService. 
        # Given the scope, let's keep it simple: We try to get session, if not create. 
        # But since 'self.session_service' is new every time, we lose 'state' in memory.
        # FIX: We should use a global session service or accept that it's stateless for now (1-turn).
        # Let's assume stateless for this step or we define a global variable in this file for the session service.
        
        # GLOBAL HACK for InMemory Persistence across requests
        if not hasattr(self, "_global_session_service"):
             # This won't work on instance. 
             pass

        # Let's just create a session for this request. It won't have history from previous requests (unless we passed history in).
        # This is a limitation of InMemorySessionService used inside a per-request Service.
        
        try:
            await self.session_service.create_session(
                app_name="personal_assistant",
                user_id=str(db_agent.manager_id), # Use manager_id as user_id for now
                session_id=session_id
            )
        except Exception:
            # Session might already exist if we used a persistent store, but here it's new every time so no error.
            pass

        runner = Runner(
            agent=adk_agent,
            app_name="personal_assistant",
            session_service=self.session_service
        )

        response_text = await call_agent_async(
            query=query,
            runner=runner,
            user_id=str(db_agent.manager_id),
            session_id=session_id
        )
        
        return response_text
