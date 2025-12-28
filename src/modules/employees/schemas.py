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

class EmployeeSearchRequest(BaseModel):
    query: str
    limit: int = 5

class EmployeeSearchResult(EmployeeRead):
    similarity_score: float
    distance: float

class EmployeeFindRequest(BaseModel):
    manager_id: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None

class EmployeeTextSearchRequest(BaseModel):
    query: str
    manager_id: Optional[UUID] = None
    limit: int = 10
