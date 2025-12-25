from dataclasses import dataclass
from src.modules.shared.domain.event import DomainEvent
from uuid import UUID

@dataclass(frozen=True)
class EmployeeCreated(DomainEvent):
    employee_id: UUID
    first_name: str
    last_name: str
    email: str
    mobile: str
