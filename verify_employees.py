import requests
import sys
import os

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

    base_url = "http://localhost:8000"
    
    # 1. Create a Manager
    print("\n1. Creating Manager...")
    manager_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "secretpassword"
    }
    response = requests.post(f"{base_url}/managers/", json=manager_data)
    manager = check(response)
    manager_id = manager["id"]
    print(f"Manager created: {manager_id}")

    # 2. Create an Employee for the Manager
    print("\n2. Creating Employee...")
    employee_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "mobile": "+1234567890",
        "email": "alice.smith@example.com",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/employees/", json=employee_data)
    employee = check(response, 201)
    print(f"Employee created: {employee['id']}")

    if employee["manager_id"] != manager_id:
        print(f"FAILED: Employee manager_id {employee['manager_id']} does not match {manager_id}")
        sys.exit(1)

    # 3. Verify Employee List
    print("\n3. Listing Employees...")
    response = requests.get(f"{base_url}/employees/")
    employees = check(response)
    print(f"Found {len(employees)} employees")
    
    found = False
    for emp in employees:
        if emp["id"] == employee["id"]:
            found = True
            break
    
    if not found:
        print("FAILED: Created employee not found in list")
        sys.exit(1)

    # 4. Verify Embedding Generation
    print("\n4. Verifying Embedding...")
    import time
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    
    # Wait for async event handler (in memory it's sync, but good practice to verify DB state separately)
    # The handler commits to DB, so we should be able to see it.
    
    print("Checking DB for embedding...")
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT embedding FROM employees WHERE id = '{employee['id']}'"))
        row = result.fetchone()
        if row and row[0]:
            # pgvector returns a string representation or list depending on driver, 
            # with sqlalchemy it might be an object or list.
            # let's just check it's not null and has length.
            embedding = row[0]
            # If it's a string, we might need to parse, but usually list with psycopg2 + pgvector
            print(f"Embedding found! Type: {type(embedding)}")
            
            import json
            actual_embedding = []
            if isinstance(embedding, str):
                # pgvector string format is '[1.0,2.0,3.0]'
                try:
                    actual_embedding = json.loads(embedding)
                except:
                    # Fallback if it's not strictly json compatible (though usually is)
                    actual_embedding = [float(x) for x in embedding.strip("[]").split(",")]
            elif hasattr(embedding, '__len__'):
                 actual_embedding = embedding
            
            print(f"Embedding dimensions: {len(actual_embedding)}")
            if len(actual_embedding) == 1536:
                 print("SUCCESS: Embedding has correct dimensions (1536).")
            else:
                 print(f"WARNING: Embedding dimensions {len(actual_embedding)} != 1536")
        else:
            print("FAILED: No embedding found for employee.")
            sys.exit(1)

    print("\nSUCCESS: Employees module verification passed!")

if __name__ == "__main__":
    main()
