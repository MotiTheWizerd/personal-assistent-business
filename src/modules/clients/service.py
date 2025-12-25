from sqlalchemy.orm import Session
from src.modules.clients.models import ClientModel
from src.modules.clients.schemas import ClientCreate
from src.modules.shared.domain.bus import EventBus
from src.modules.clients.events import ClientCreated

class ClientService:
    def __init__(self, db: Session, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus

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
