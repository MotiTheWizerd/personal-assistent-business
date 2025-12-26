import requests
import sys
import uuid
import time
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.modules.embeddings.service import GeminiEmbeddingService
from src.database import Base
from dotenv import load_dotenv

# Load env to get DB URL and API Key
load_dotenv()

def main():
    print("Debugging Similarity Score...")
    
    # 1. Setup DB connection directly to bypass API filter for investigation
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 2. Setup Embedding Service
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set")
        return
    embedding_service = GeminiEmbeddingService(api_key=api_key)

    # 3. Create 'Test' Employee directly in DB (or ensure one exists)
    # We will compute distance manually for a hypothetical "Test" employee
    
    # Text that is embedded for employee: "{first_name} | {last_name} | {email} | {mobile}"
    # Example for a user named "Test"
    employee_text = "Test | User | test.user@example.com | +1234567890"
    print(f"Simulating Employee Embedding for text: '{employee_text}'")
    
    emp_embedding = embedding_service.embed_text(employee_text)
    
    # 4. Create Query Embedding
    query = "test"
    print(f"Generating embedding for query: '{query}'")
    query_embedding = embedding_service.embed_text(query)
    
    # 5. Calculate Cosine Similarity manually
    # Cosine Similarity = dot_product(A, B) / (norm(A) * norm(B))
    # Using pgvector or numpy
    import numpy as np
    
    vec_a = np.array(emp_embedding)
    vec_b = np.array(query_embedding)
    
    # Cosine Distance = 1 - Cosine Similarity
    # Creating simple cosine similarity function
    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    similarity = dot / (norm_a * norm_b)
    
    distance = 1 - similarity
    
    print("-" * 30)
    print(f"Calculated Similarity Score: {similarity:.4f}")
    print(f"Calculated Distance: {distance:.4f}")
    print("-" * 30)
    
    if similarity < 0.695:
        print(f"ALERT: Score {similarity:.4f} is BELOW the threshold of 0.695.")
        print("This explains why it is not returning results.")
    else:
        print(f"Score {similarity:.4f} is ABOVE the threshold. It should have been returned.")

if __name__ == "__main__":
    main()
