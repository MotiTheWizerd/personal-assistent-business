from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class ManagerBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    default_rate: float = 37.0

class ManagerCreate(ManagerBase):
    password: str

class ManagerRead(ManagerBase):
    id: UUID
    default_rate: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
