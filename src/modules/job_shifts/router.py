from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.database import get_db
from src.modules.job_shifts.schemas import JobShiftCreate, JobShiftRead
from src.modules.job_shifts.service import JobShiftService

def get_service(db: Session = Depends(get_db)) -> JobShiftService:
    return JobShiftService(db)

router = APIRouter(
    prefix="/job_shifts",
    tags=["job_shifts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=JobShiftRead, status_code=status.HTTP_201_CREATED)
def create_shift(
    shift: JobShiftCreate, 
    service: JobShiftService = Depends(get_service)
):
    # In a real app we would verify that manager_id, client_id, employee_id exist
    return service.create_shift(shift=shift)

@router.get("/", response_model=List[JobShiftRead])
def read_shifts(skip: int = 0, limit: int = 100, service: JobShiftService = Depends(get_service)):
    return service.get_shifts(skip=skip, limit=limit)
