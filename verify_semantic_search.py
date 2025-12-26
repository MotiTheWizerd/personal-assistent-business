import requests
import sys
import uuid
import time
import random

BASE_URL = "http://localhost:8000"

def check(response, expected_status=200):
    if response.status_code != expected_status:
        print(f"FAILED: Expected {expected_status}, got {response.status_code}")
        print(response.text)
        sys.exit(1)
    return response.json()

def main():
    print("Starting Semantic Search Verification...")
    
    # 1. Create a Helper Manager
    unique_id = str(uuid.uuid4())[:8]
    manager_data = {
        "first_name": "Search",
        "last_name": "Tester",
        "username": f"tester_{unique_id}",
        "email": f"tester_{unique_id}@example.com",
        "password": "password123"
    }
    print(f"\n1. Creating Manager ({manager_data['username']})...")
    resp = requests.post(f"{BASE_URL}/managers/", json=manager_data)
    manager = check(resp, 200) # Manager creation might return 200 or 201
    manager_id = manager["id"]
    print(f"Manager created: {manager_id}")

    # 2. Create Target Employee
    # Embedding is generated from: first_name | last_name | email | mobile
    # We'll use values that represent a specific role we can search for.
    employee_data = {
        "first_name": "Python",
        "last_name": "Developer",
        "mobile": "+15550001234",
        "email": f"python.dev.{unique_id}@example.com",
        "manager_id": manager_id
    }
    print(f"\n2. Creating Employee 'Python Developer'...")
    resp = requests.post(f"{BASE_URL}/employees/", json=employee_data)
    employee = check(resp, 201)
    print(f"Employee created: {employee['id']}")
    
    # The embedding generation is handled by the event bus.
    # If the event bus is synchronous (InMemoryEventBus in main.py), 
    # the embedding should be ready immediately after the request returns.
    # But just in case of any async processing or lag:
    print("Waiting 2 seconds for embedding generation...")
    time.sleep(2)

    # 3. Perform Semantic Search
    query = "software engineer coding python"
    print(f"\n3. Searching for '{query}'...")
    
    search_payload = {
        "query": query,
        "limit": 5
    }
    
    resp = requests.post(f"{BASE_URL}/employees/general-semantic-search", json=search_payload)
    results = check(resp, 200)
    
    print(f"Found {len(results)} employees.")
    
    # 4. Verify Results
    found = False
    # 4. Verify Results
    found = False
    for emp in results:
        score = emp.get("similarity_score", "N/A")
        distance = emp.get("distance", "N/A")
        print(f" - {emp['first_name']} {emp['last_name']} ({emp['email']}) | Score: {score} | Distance: {distance}")
        if emp["id"] == employee["id"]:
            found = True
    
    if found:
        print("\nSUCCESS: Created employee found via semantic search!")
    else:
        print("\nFAILURE: Created employee NOT found in search results.")
        # Debugging: print first few if any
        if not results:
             print("No results returned.")
        sys.exit(1)

    # 5. Verify Client Semantic Search
    print("\n" + "="*50)
    print("5. Verifying Client Semantic Search...")
    print("="*50)
    
    # Create a Client
    client_data = {
        "client_name": "ACME Corp",
        "email": f"contact.{unique_id}@acme.com",
        "mobile": "+19998887777",
        "client_description": "A leading provider of road runner catching equipment.",
        "manager_id": manager_id
    }
    print(f"\nCreating Client '{client_data['client_name']}'...")
    resp = requests.post(f"{BASE_URL}/clients/", json=client_data)
    client = check(resp, 201)
    print(f"Client created: {client['id']}")
    
    print("Waiting 2 seconds for embedding generation...")
    time.sleep(2)
    
    # Search for Client
    client_query = "catch road runner"
    print(f"\nSearching for '{client_query}'...")
    search_payload = {
        "query": client_query,
        "limit": 5
    }
    
    resp = requests.post(f"{BASE_URL}/clients/general-semantic-search", json=search_payload)
    results = check(resp, 200)
    
    print(f"Found {len(results)} clients.")
    
    found_client = False
    for cli in results:
        score = cli.get("similarity_score", "N/A")
        distance = cli.get("distance", "N/A")
        print(f" - {cli['client_name']} ({cli['email']}) | Score: {score} | Distance: {distance}")
        if cli["id"] == client["id"]:
            found_client = True
            
    if found_client:
        print("\nSUCCESS: Created client found via semantic search!")
    else:
        print("\nFAILURE: Created client NOT found in search results.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\nERROR: Could not connect to {BASE_URL}. Is the server running?")
        sys.exit(1)
