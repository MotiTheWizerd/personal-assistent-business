from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class ClientBase(BaseModel):
    client_name: str
    mobile: str
    email: EmailStr
    client_description: str
    default_rate: float = 0.0

class ClientCreate(ClientBase):
    manager_id: UUID

class ClientRead(ClientBase):
    id: UUID
    manager_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClientSearchRequest(BaseModel):
    query: str
    limit: int = 5

class ClientSearchResult(ClientRead):
    similarity_score: float
    distance: float

class ClientFindRequest(BaseModel):
    manager_id: Optional[UUID] = None
    client_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    client_description: Optional[str] = None

class ClientTextSearchRequest(BaseModel):
    query: str
    manager_id: Optional[UUID] = None
    limit: int = 10
