from sqlalchemy.orm import Session
from src.modules.clients.events import ClientCreated
from src.modules.embeddings.service import GeminiEmbeddingService
from src.modules.clients.models import ClientModel
from src.database import SessionLocal 

class ClientEmbeddingHandler:
    def __init__(self, embedding_service: GeminiEmbeddingService):
        self.embedding_service = embedding_service

    def handle(self, event: ClientCreated):
        text_to_embed = f"{event.client_name} | {event.mobile} | {event.email} | {event.client_description}"
        print(f"Generating embedding for client: {text_to_embed}")
        
        try:
            embedding_vector = self.embedding_service.embed_text(text_to_embed)
            
            db: Session = SessionLocal()
            try:
                stmt = (
                    ClientModel.__table__
                    .update()
                    .where(ClientModel.id == event.client_id)
                    .values(embedding=embedding_vector)
                )
                db.execute(stmt)
                db.commit()
                print(f"Updated embedding for client {event.client_id}")
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error generating/saving embedding for client {event.client_id}: {e}")
