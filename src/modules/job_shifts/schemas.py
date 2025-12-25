from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class JobShiftBase(BaseModel):
    start_date: datetime
    end_date: datetime
    is_paid: bool = False

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
