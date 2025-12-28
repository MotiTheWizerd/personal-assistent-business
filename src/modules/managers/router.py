from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.modules.auth.security import create_access_token, get_current_manager
from src.modules.managers.schemas import ManagerCreate, ManagerLogin, ManagerRead, Token
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
def read_managers(
    skip: int = 0,
    limit: int = 100,
    service: ManagerService = Depends(get_service),
    _current_manager=Depends(get_current_manager),
):
    return service.get_managers(skip=skip, limit=limit)

@router.post("/login", response_model=Token)
def login_manager(payload: ManagerLogin, service: ManagerService = Depends(get_service)):
    manager = service.authenticate_manager(email=payload.email, password=payload.password)
    if not manager:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(manager)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=ManagerRead)
def read_current_manager(current_manager=Depends(get_current_manager)):
    return current_manager
