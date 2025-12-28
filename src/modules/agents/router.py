from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.database import get_db
from src.modules.agents.schemas import AgentCreate, AgentRead, AgentChatRequest, AgentChatResponse
from src.modules.agents.service import AgentService

def get_service(db: Session = Depends(get_db)) -> AgentService:
    return AgentService(db)

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent: AgentCreate, 
    service: AgentService = Depends(get_service)
):
    return service.create_agent(agent_data=agent)

@router.get("/{agent_id}", response_model=AgentRead)
def read_agent(
    agent_id: UUID, 
    service: AgentService = Depends(get_service)
):
    return service.get_agent(agent_id=agent_id)

@router.post("/{agent_id}/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    agent_id: UUID,
    chat_request: AgentChatRequest,
    service: AgentService = Depends(get_service)
):
    response = await service.chat_with_agent(
        agent_id=agent_id,
        query=chat_request.query,
        session_id=chat_request.session_id
    )
    return AgentChatResponse(response=response)
