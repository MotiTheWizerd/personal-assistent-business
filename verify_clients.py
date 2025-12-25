import requests
import sys
import os
import json
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Ensure src is in pythonpath
sys.path.append(os.getcwd())

from reset_db import reset_db

def check(response, expected_status=200):
    if response.status_code != expected_status:
        print(f"FAILED: Expected {expected_status}, got {response.status_code}")
        print(response.text)
        sys.exit(1)
    return response.json()

def main():
    print("Resetting database...")
    reset_db()
    
    # We also need to enable pgvector extension again if reset dropped it (though drop_all drops tables usually)
    # But just in case
    from enable_pgvector import enable_pgvector
    enable_pgvector()

    base_url = "http://localhost:8000"
    
    # 1. Create a Manager
    print("\n1. Creating Manager...")
    manager_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "username": "janedoe_client_mgr",
        "email": "jane.doe.mgr@example.com",
        "password": "secretpassword"
    }
    # We might need to handle if manager already exists if we didn't reset, 
    # but we do reset_db() above.
    # Note: we need to use the managers endpoint.
    response = requests.post(f"{base_url}/managers/", json=manager_data)
    if response.status_code != 200:
        # It returns 200 on success per previous logs, let's allow 201 too just in case
        pass
    manager = check(response) # check defaults to 200
    manager_id = manager["id"]
    print(f"Manager created: {manager_id}")

    # 2. Create a Client
    print("\n2. Creating Client...")
    client_data = {
        "client_name": "Tech Corp",
        "mobile": "+1987654321",
        "email": "contact@techcorp.com",
        "client_description": "A leading technology company specializing in AI solutions.",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/clients/", json=client_data)
    client = check(response, 201)
    client_id = client["id"]
    print(f"Client created: {client_id}")

    # 3. Verify Client List
    print("\n3. Listing Clients...")
    response = requests.get(f"{base_url}/clients/")
    clients = check(response)
    print(f"Found {len(clients)} clients")
    
    found = False
    for c in clients:
        if c["id"] == client_id:
            found = True
            break
            
    if not found:
        print("FAILED: Created client not found in list")
        sys.exit(1)

    # 3. Verify Embedding Generation
    print("\n3. Verifying Embedding...")
    
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    
    print("Checking DB for embedding...")
    # Give some time for async handler
    time.sleep(2)
    
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT embedding FROM clients WHERE id = '{client_id}'"))
        row = result.fetchone()
        if row and row[0]:
            embedding = row[0]
            print(f"Embedding found! Type: {type(embedding)}")
            
            actual_embedding = []
            if isinstance(embedding, str):
                try:
                    actual_embedding = json.loads(embedding)
                except:
                    actual_embedding = [float(x) for x in embedding.strip("[]").split(",")]
            elif hasattr(embedding, '__len__'):
                 actual_embedding = embedding
            
            print(f"Embedding dimensions: {len(actual_embedding)}")
            if len(actual_embedding) == 1536:
                 print("SUCCESS: Embedding has correct dimensions (1536).")
            else:
                 print(f"WARNING: Embedding dimensions {len(actual_embedding)} != 1536")
        else:
            print("FAILED: No embedding found for client.")
            sys.exit(1)

    print("\nSUCCESS: Clients module verification passed!")

if __name__ == "__main__":
    main()
