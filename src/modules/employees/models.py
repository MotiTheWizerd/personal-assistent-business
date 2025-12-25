import uuid
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class EmployeeModel(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    nickname = Column(String, nullable=True)
    mobile = Column(String)
    email = Column(String, unique=True, index=True)
    default_rate = Column(Float, default=0.0)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("managers.id"))
    embedding = Column(Vector(1536))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    manager = relationship("ManagerModel", back_populates="employees")
