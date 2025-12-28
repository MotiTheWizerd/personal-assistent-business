from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.modules.clients.models import ClientModel
from src.modules.clients.schemas import ClientCreate
from src.modules.shared.domain.bus import EventBus
from src.modules.clients.events import ClientCreated
from uuid import UUID
from src.modules.embeddings.service import GeminiEmbeddingService

class ClientService:
    def __init__(self, db: Session, event_bus: EventBus, embedding_service: GeminiEmbeddingService):
        self.db = db
        self.event_bus = event_bus
        self.embedding_service = embedding_service

    def create_client(self, client: ClientCreate) -> ClientModel:
        db_client = ClientModel(
            **client.model_dump()
        )
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        
        event = ClientCreated(
            client_id=db_client.id,
            client_name=db_client.client_name,
            mobile=db_client.mobile,
            email=db_client.email,
            client_description=db_client.client_description
        )
        self.event_bus.publish(event)
        
        return db_client

    def get_clients(self, skip: int = 0, limit: int = 100) -> list[ClientModel]:
        return self.db.query(ClientModel).offset(skip).limit(limit).all()

    def get_client_by_email(self, email: str) -> ClientModel | None:
        return self.db.query(ClientModel).filter(ClientModel.email == email).first()

    def search_clients(self, query: str, limit: int = 5) -> list[ClientModel]:
        # Generate embedding for the query
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search for similar clients using cosine distance
        distance_col = ClientModel.embedding.cosine_distance(query_embedding)
        
        results = self.db.query(ClientModel, distance_col)\
            .order_by(distance_col)\
            .limit(limit)\
            .all()
        
        # Convert to list of dicts with similarity score and distance
        return [
            {
                **client.__dict__, 
                "similarity_score": 1 - distance,
                "distance": distance
            }
            for client, distance in results
        ]

    def get_clients_by_params(
        self,
        manager_id: UUID = None,
        client_name: str = None,
        email: str = None,
        mobile: str = None,
        client_description: str = None
    ) -> list[ClientModel]:
        query = self.db.query(ClientModel)
        
        if manager_id:
            query = query.filter(ClientModel.manager_id == manager_id)
        if client_name:
            query = query.filter(ClientModel.client_name.ilike(f"%{client_name}%"))
        if email:
            query = query.filter(ClientModel.email.ilike(f"%{email}%"))
        if mobile:
            query = query.filter(ClientModel.mobile.ilike(f"%{mobile}%"))
        if client_description:
            query = query.filter(ClientModel.client_description.ilike(f"%{client_description}%"))
            
        return query.all()

    def search_clients_text(
        self,
        query: str,
        manager_id: UUID = None,
        limit: int = 10
    ) -> list[ClientModel]:
        base_query = self.db.query(ClientModel)

        if manager_id:
            base_query = base_query.filter(ClientModel.manager_id == manager_id)

        text_filter = or_(
            ClientModel.client_name.ilike(f"%{query}%"),
            ClientModel.email.ilike(f"%{query}%"),
            ClientModel.mobile.ilike(f"%{query}%"),
            ClientModel.client_description.ilike(f"%{query}%")
        )

        return base_query.filter(text_filter).limit(limit).all()
