from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    model: str
    instruction: Optional[str] = ""

class AgentCreate(AgentBase):
    manager_id: UUID

class AgentRead(AgentBase):
    id: UUID
    manager_id: UUID

    class Config:
        from_attributes = True

class AgentChatRequest(BaseModel):
    query: str
    session_id: str = "default_session"

class AgentChatResponse(BaseModel):
    response: str
