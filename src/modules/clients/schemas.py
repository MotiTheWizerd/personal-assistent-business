from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class ClientBase(BaseModel):
    client_name: str
    mobile: str
    email: EmailStr
    client_description: str

class ClientCreate(ClientBase):
    manager_id: UUID

class ClientRead(ClientBase):
    id: UUID
    manager_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
