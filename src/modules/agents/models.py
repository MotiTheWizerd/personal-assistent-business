import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    model = Column(String) 
    instruction = Column(String, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("managers.id"))

    manager = relationship("ManagerModel", back_populates="agents")
