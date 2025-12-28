import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.database import Base

class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_name = Column(String, index=True)
    mobile = Column(String)
    email = Column(String, unique=True, index=True)
    client_description = Column(String)
    default_rate = Column(Float, default=0.0)
    
    manager_id = Column(UUID(as_uuid=True), ForeignKey("managers.id"))
    manager = relationship("ManagerModel", back_populates="clients")
    
    embedding = Column(Vector(1536))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
