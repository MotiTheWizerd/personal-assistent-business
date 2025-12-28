# Personal Assistant - Smart Scheduler API

Welcome to the **Personal Assistant** project. This is an AI-aware, event-driven employee management backend that turns natural language intent into structured scheduling data.

## Project Overview

Personal Assistant bridges flexible communication (WhatsApp) and structured management.
- **The Core Idea**: Managers can send natural language messages via WhatsApp (e.g., *"Set Moti Sunday to Thursday 8 hours at Hi-Towers"*) which are processed by an LLM and converted into actionable scheduling data.
- **The Result**: A low-friction, smart backoffice that removes the heavy lifting of manual data entry and schedule tracking.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Vector Search**: pgvector
- **LLM/Embeddings**: Gemini (via google-adk) and LiteLLM
- **Config**: python-dotenv
- **Security**: Argon2 + Passlib
- **Architecture**: Event-Driven & Ultra-Modular

## Architectural Principles

### 1. Event-Driven Architecture
The backend uses an in-memory event bus to keep modules decoupled while still reacting to changes:
- Entity events (e.g., employees or clients created) trigger embedding generation.
- Handlers integrate external services without coupling core modules.

### 2. Modular Domain Design
Features are organized into domain modules (managers, employees, clients, job shifts, agents) with clear routers and handlers.

### 3. AI-First Workflow
The system is built to accept natural language intent, then enrich and index records for fast lookup and retrieval.

## Quick Start

```bash
# Install dependencies
poetry install

# Run the API server
poetry run uvicorn src.main:app --reload
```

The API root is available at `http://localhost:8000/` and docs at `http://localhost:8000/docs`.

---
Built with love by the Quantum Team (Moti(User), Codex(AI), Gemini(AI), Claude(AI)).
