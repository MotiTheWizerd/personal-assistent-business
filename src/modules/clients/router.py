from fastapi import APIRouter, Depends, HTTPException, status
import os
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.modules.clients.schemas import ClientCreate, ClientRead, ClientSearchRequest, ClientSearchResult, ClientFindRequest, ClientTextSearchRequest
from src.modules.clients.service import ClientService
from src.modules.shared.domain.bus import EventBus
from src.modules.embeddings.service import GeminiEmbeddingService

# Defer import of event_bus to avoid circular dependency, same pattern as employees
def get_event_bus():
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
) -> ClientService:
    return ClientService(db, event_bus, embedding_service)

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

@router.post("/general-semantic-search", response_model=List[ClientSearchResult])
def search_clients(
    request: ClientSearchRequest,
    service: ClientService = Depends(get_service)
):
    """
    Search for clients using semantic search on their profile embedding.
    """
    return service.search_clients(query=request.query, limit=request.limit)

@router.post("/text-search", response_model=List[ClientRead])
def search_clients_text(
    request: ClientTextSearchRequest,
    service: ClientService = Depends(get_service)
):
    return service.search_clients_text(
        query=request.query,
        manager_id=request.manager_id,
        limit=request.limit
    )

@router.post("/FindClients", response_model=List[ClientRead])
def find_clients(
    search_params: ClientFindRequest,
    service: ClientService = Depends(get_service)
):
    """
    Find clients based on various parameters (manager_id, client_name, email, mobile, client_description).
    """
    return service.get_clients_by_params(
        manager_id=search_params.manager_id,
        client_name=search_params.client_name,
        email=search_params.email,
        mobile=search_params.mobile,
        client_description=search_params.client_description
    )
