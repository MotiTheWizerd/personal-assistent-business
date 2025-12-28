from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class JobShiftBase(BaseModel):
    start_date: datetime
    end_date: datetime
    is_paid: bool = False
    effective_rate: Optional[float] = None

class JobShiftCreate(JobShiftBase):
    manager_id: UUID
    client_id: UUID
    employee_id: UUID

class JobShiftRead(JobShiftBase):
    id: UUID
    manager_id: UUID
    client_id: UUID
    employee_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScheduleClient(BaseModel):
    id: UUID
    client_name: str
    email: str
    mobile: str

    class Config:
        from_attributes = True

class ScheduleEmployee(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    nickname: Optional[str] = None
    email: str
    mobile: str

    class Config:
        from_attributes = True

class JobShiftScheduleRead(JobShiftBase):
    id: UUID
    manager_id: UUID
    client_id: UUID
    employee_id: UUID
    client: ScheduleClient
    employee: ScheduleEmployee
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobShiftSearch(BaseModel):
    manager_id: UUID
    employee_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ScheduleSearch(BaseModel):
    manager_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
