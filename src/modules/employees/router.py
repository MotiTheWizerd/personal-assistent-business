from fastapi import APIRouter, Depends, HTTPException, status
import os
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.database import get_db
from src.modules.employees.schemas import EmployeeCreate, EmployeeRead, EmployeeSearchRequest, EmployeeSearchResult
from src.modules.employees.service import EmployeeService
from src.modules.embeddings.service import GeminiEmbeddingService

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    responses={404: {"description": "Not found"}},
)

from src.modules.shared.domain.bus import EventBus

# Dependency injection for EventBus, in a real app this would be more sophisticated
# For now we will rely on a global or app-state based bus, or pass it via dependency overrides
# But to keep it simple and working with the existing pattern:

def get_event_bus():
    # Deferred import to avoid circular dependency
    from src.main import event_bus
    return event_bus

def get_embedding_service():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    return GeminiEmbeddingService(api_key=api_key)

def get_service(
    db: Session = Depends(get_db), 
    event_bus: EventBus = Depends(get_event_bus),
    embedding_service: GeminiEmbeddingService = Depends(get_embedding_service)
) -> EmployeeService:
    return EmployeeService(db, event_bus, embedding_service)

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    service: EmployeeService = Depends(get_service)
):
    db_employee = service.get_employee_by_email(email=employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Note: In a real app we might verify manager_id exists here or let FK constraint handle it (handling exception)
    # For now we assume manager_id is valid or let DB error
    return service.create_employee(employee=employee)

@router.get("/", response_model=List[EmployeeRead])
def read_employees(skip: int = 0, limit: int = 100, service: EmployeeService = Depends(get_service)):
    return service.get_employees(skip=skip, limit=limit)

@router.post("/general-semantic-search", response_model=List[EmployeeSearchResult])
def search_employees(
    request: EmployeeSearchRequest,
    service: EmployeeService = Depends(get_service)
):
    """
    Search for employees using semantic search on their profile embedding.
    """
    return service.search_employees(query=request.query, limit=request.limit)
