from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.modules.employees.models import EmployeeModel
from src.modules.employees.schemas import EmployeeCreate
from src.modules.shared.domain.bus import EventBus
from src.modules.employees.events import EmployeeCreated
from uuid import UUID
from src.modules.embeddings.service import GeminiEmbeddingService

class EmployeeService:
    def __init__(self, db: Session, event_bus: EventBus, embedding_service: GeminiEmbeddingService):
        self.db = db
        self.event_bus = event_bus
        self.embedding_service = embedding_service

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

    def search_employees(self, query: str, limit: int = 5) -> list[EmployeeModel]:
        # Generate embedding for the query
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search for similar employees using cosine distance
        # Note: pgvector's cosine_distance operator is <=>
        distance_col = EmployeeModel.embedding.cosine_distance(query_embedding)
        
        # Filter for similarity score > 0.695 (distance < 0.305)
        # We can do this in the query or in python. Doing it in query is more efficient.
        # But for compatibility with limit, we should filter first.
        # Disabled filtering per user request
        results = self.db.query(EmployeeModel, distance_col)\
            .order_by(distance_col)\
            .limit(limit)\
            .all()
        
        # Convert to list of dicts with similarity score and distance
        return [
            {
                **employee.__dict__, 
                "similarity_score": 1 - distance,
                "distance": distance
            }
            for employee, distance in results
        ]

    def get_employees_by_params(
        self,
        manager_id: UUID,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        nickname: str = None
    ) -> list[EmployeeModel]:
        query = self.db.query(EmployeeModel)
        
        if manager_id:
            query = query.filter(EmployeeModel.manager_id == manager_id)
        if first_name:
            query = query.filter(EmployeeModel.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.filter(EmployeeModel.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(EmployeeModel.email.ilike(f"%{email}%"))
        if nickname:
            query = query.filter(EmployeeModel.nickname.ilike(f"%{nickname}%"))
            
        return query.all()

    def search_employees_text(
        self,
        query: str,
        manager_id: UUID = None,
        limit: int = 10
    ) -> list[EmployeeModel]:
        base_query = self.db.query(EmployeeModel)

        if manager_id:
            base_query = base_query.filter(EmployeeModel.manager_id == manager_id)

        text_filter = or_(
            EmployeeModel.first_name.ilike(f"%{query}%"),
            EmployeeModel.last_name.ilike(f"%{query}%"),
            EmployeeModel.nickname.ilike(f"%{query}%")
        )

        return base_query.filter(text_filter).limit(limit).all()
