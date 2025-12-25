from sqlalchemy.orm import Session
from src.modules.employees.models import EmployeeModel
from src.modules.employees.schemas import EmployeeCreate
from src.modules.shared.domain.bus import EventBus
from src.modules.employees.events import EmployeeCreated

class EmployeeService:
    def __init__(self, db: Session, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus

    def create_employee(self, employee: EmployeeCreate) -> EmployeeModel:
        db_employee = EmployeeModel(
            **employee.model_dump()
        )
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        
        event = EmployeeCreated(
            employee_id=db_employee.id,
            first_name=db_employee.first_name,
            last_name=db_employee.last_name,
            email=db_employee.email,
            mobile=db_employee.mobile
        )
        self.event_bus.publish(event)
        
        return db_employee

    def get_employees(self, skip: int = 0, limit: int = 100) -> list[EmployeeModel]:
        return self.db.query(EmployeeModel).offset(skip).limit(limit).all()

    def get_employee_by_email(self, email: str) -> EmployeeModel | None:
        return self.db.query(EmployeeModel).filter(EmployeeModel.email == email).first()
