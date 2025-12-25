import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Ensure src is in pythonpath
sys.path.append(os.getcwd())

load_dotenv()

def enable_pgvector():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        return

    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("Enabling pgvector extension...")
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("pgvector extension enabled.")
        except Exception as e:
            print(f"Error enabling pgvector: {e}")

if __name__ == "__main__":
    enable_pgvector()
