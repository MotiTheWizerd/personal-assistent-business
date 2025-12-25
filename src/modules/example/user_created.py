from dataclasses import dataclass
from src.modules.shared.domain.event import DomainEvent

@dataclass(frozen=True)
class UserCreated(DomainEvent):
    username: str
    email: str
