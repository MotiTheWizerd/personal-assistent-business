import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.database import Base

class JobShiftModel(Base):
    __tablename__ = "job_shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("managers.id"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    is_paid = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    manager = relationship("ManagerModel")
    client = relationship("ClientModel")
    employee = relationship("EmployeeModel")
