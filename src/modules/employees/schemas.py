from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    nickname: Optional[str] = None
    mobile: str
    email: EmailStr
    default_rate: float = 0.0

class EmployeeCreate(EmployeeBase):
    manager_id: UUID

class EmployeeRead(EmployeeBase):
    id: UUID
    default_rate: float
    manager_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
