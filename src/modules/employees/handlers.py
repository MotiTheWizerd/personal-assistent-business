from sqlalchemy.orm import Session
from src.modules.employees.events import EmployeeCreated
from src.modules.embeddings.service import GeminiEmbeddingService
from src.modules.employees.models import EmployeeModel
from src.database import SessionLocal # Using SessionLocal directly for simplicity in handler

class EmployeeEmbeddingHandler:
    def __init__(self, embedding_service: GeminiEmbeddingService):
        self.embedding_service = embedding_service

    def handle(self, event: EmployeeCreated):
        text_to_embed = f"{event.first_name} | {event.last_name} | {event.email} | {event.mobile}"
        print(f"Generating embedding for text: {text_to_embed}")
        
        try:
            embedding_vector = self.embedding_service.embed_text(text_to_embed)
            
            # Update employee with embedding
            # In a real event bus this might be in a separate process/thread
            # Ideally we'd dependency inject the DB session provider
            db: Session = SessionLocal()
            try:
                # We need to fetch the employee again to update it
                # Using the ID from the event
                # Note: models.py needs to be imported for this to work
                # We are directly updating the specific employee row
                stmt = (
                    EmployeeModel.__table__
                    .update()
                    .where(EmployeeModel.id == event.employee_id)
                    .values(embedding=embedding_vector)
                )
                db.execute(stmt)
                db.commit()
                print(f"Updated embedding for employee {event.employee_id}")
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error generating/saving embedding for employee {event.employee_id}: {e}")
