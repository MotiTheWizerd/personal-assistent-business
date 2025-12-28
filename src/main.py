import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.database import engine, Base
from src.modules.managers.router import router as managers_router
from src.modules.employees.router import router as employees_router
from src.modules.clients.router import router as clients_router
from src.modules.shared.domain.bus import InMemoryEventBus
from src.modules.employees.events import EmployeeCreated
from src.modules.employees.handlers import EmployeeEmbeddingHandler
from src.modules.clients.events import ClientCreated
from src.modules.clients.handlers import ClientEmbeddingHandler
from src.modules.embeddings.service import GeminiEmbeddingService

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Assistant API",
    description="API for Personal Assistant application",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Event Bus
event_bus = InMemoryEventBus()

# Initialize Services and Handlers
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    embedding_service = GeminiEmbeddingService(api_key=api_key)
    
    # Handlers
    employee_embedding_handler = EmployeeEmbeddingHandler(embedding_service)
    client_embedding_handler = ClientEmbeddingHandler(embedding_service)
    
    # Register Handlers
    event_bus.subscribe(EmployeeCreated, employee_embedding_handler.handle)
    event_bus.subscribe(ClientCreated, client_embedding_handler.handle)
else:
    print("WARNING: GEMINI_API_KEY not found. Embeddings will not be generated.")

app.include_router(managers_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(clients_router, prefix="/api")
from src.modules.job_shifts.router import router as job_shifts_router
app.include_router(job_shifts_router, prefix="/api")

from src.modules.agents.router import router as agents_router
app.include_router(agents_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Personal Assistant API"}
