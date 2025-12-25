from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.modules.clients.schemas import ClientCreate, ClientRead
from src.modules.clients.service import ClientService
from src.modules.shared.domain.bus import EventBus

# Defer import of event_bus to avoid circular dependency, same pattern as employees
def get_event_bus():
    from src.main import event_bus
    return event_bus

def get_service(db: Session = Depends(get_db), event_bus: EventBus = Depends(get_event_bus)) -> ClientService:
    return ClientService(db, event_bus)

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    client: ClientCreate, 
    service: ClientService = Depends(get_service)
):
    db_client = service.get_client_by_email(email=client.email)
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_client(client=client)

@router.get("/", response_model=List[ClientRead])
def read_clients(skip: int = 0, limit: int = 100, service: ClientService = Depends(get_service)):
    return service.get_clients(skip=skip, limit=limit)
