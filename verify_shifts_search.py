import requests
import sys
import os
import json
from datetime import datetime, timedelta

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
        "first_name": "Search",
        "last_name": "Manager",
        "username": "search_mgr",
        "email": "search.mgr@example.com",
        "password": "secretpassword"
    }
    response = requests.post(f"{base_url}/managers/", json=manager_data)
    manager = check(response)
    manager_id = manager["id"]
    
    # 2. Create a Client
    print("2. Creating Client...")
    client_data = {
        "client_name": "Search Corp",
        "mobile": "+1999888777",
        "email": "contact@searchcorp.com",
        "client_description": "Search test client",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/clients/", json=client_data, headers={"Content-Type": "application/json"})
    client = check(response, 201)
    client_id = client["id"]

    # 3. Create an Employee
    print("3. Creating Employee...")
    employee_data = {
        "first_name": "Search",
        "last_name": "Worker",
        "nickname": "Searchy",
        "mobile": "+1555666777",
        "email": "search.worker@example.com",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/employees/", json=employee_data)
    employee = check(response, 201)
    employee_id = employee["id"]

    # 4. Create 3 shifts
    print("4. Creating 3 job shifts...")
    now = datetime.now()
    times = [
        now + timedelta(hours=1),      # Today
        now + timedelta(days=10),      # In 10 days
        now + timedelta(days=40)       # In 40 days
    ]
    
    for t in times:
        shift_data = {
            "manager_id": manager_id,
            "client_id": client_id,
            "employee_id": employee_id,
            "start_date": t.isoformat(),
            "end_date": (t + timedelta(hours=8)).isoformat(),
            "is_paid": False
        }
        response = requests.post(f"{base_url}/job_shifts/", json=shift_data)
        check(response, 201)

    # 5. Test FindShifts with defaults
    print("\n5. Testing FindShifts with defaults (expecting 2 shifts within 30 days)...")
    search_data = {
        "manager_id": manager_id,
        "employee_id": employee_id
    }
    response = requests.post(f"{base_url}/job_shifts/FindShifts", json=search_data)
    results = check(response)
    print(f"Found {len(results)} shifts")
    if len(results) != 2:
        print(f"FAILED: Expected 2 shifts, found {len(results)}")
        sys.exit(1)

    # 6. Test with explicit range (future)
    print("6. Testing with explicit range (day 35 to 45)...")
    search_data = {
        "manager_id": manager_id,
        "employee_id": employee_id,
        "start_date": (now + timedelta(days=35)).isoformat(),
        "end_date": (now + timedelta(days=45)).isoformat()
    }
    response = requests.post(f"{base_url}/job_shifts/FindShifts", json=search_data)
    results = check(response)
    print(f"Found {len(results)} shifts")
    if len(results) != 1:
        print(f"FAILED: Expected 1 shift, found {len(results)}")
        sys.exit(1)

    # 7. Test with optional client_id
    print("7. Testing with optional client_id...")
    search_data = {
        "manager_id": manager_id,
        "client_id": client_id
    }
    response = requests.post(f"{base_url}/job_shifts/FindShifts", json=search_data)
    results = check(response)
    print(f"Found {len(results)} shifts (weighted by manager/client)...")
    if len(results) != 2:
        print(f"FAILED: Expected 2 shifts, found {len(results)}")
        sys.exit(1)

    print("\nSUCCESS: FindShifts verification passed!")

if __name__ == "__main__":
    main()
