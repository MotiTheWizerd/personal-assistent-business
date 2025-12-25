from dataclasses import dataclass
from src.modules.shared.domain.event import DomainEvent
from uuid import UUID

@dataclass(frozen=True, kw_only=True)
class ClientCreated(DomainEvent):
    client_id: UUID
    client_name: str
    mobile: str
    email: str
    client_description: str
