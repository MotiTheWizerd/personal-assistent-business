from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.modules.managers.schemas import ManagerCreate, ManagerRead
from src.modules.managers.service import ManagerService

router = APIRouter(
    prefix="/managers",
    tags=["managers"],
    responses={404: {"description": "Not found"}},
)

def get_service(db: Session = Depends(get_db)) -> ManagerService:
    return ManagerService(db)

@router.post("/", response_model=ManagerRead)
def create_manager(manager: ManagerCreate, service: ManagerService = Depends(get_service)):
    db_manager = service.get_manager_by_email(email=manager.email)
    if db_manager:
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_manager(manager=manager)

@router.get("/", response_model=List[ManagerRead])
def read_managers(skip: int = 0, limit: int = 100, service: ManagerService = Depends(get_service)):
    return service.get_managers(skip=skip, limit=limit)
