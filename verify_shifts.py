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
    
    # Enable pgvector just in case
    from enable_pgvector import enable_pgvector
    enable_pgvector()

    base_url = "http://localhost:8000"
    
    # 1. Create a Manager
    print("\n1. Creating Manager...")
    manager_data = {
        "first_name": "Shift",
        "last_name": "Manager",
        "username": "shift_mgr",
        "email": "shift.mgr@example.com",
        "password": "secretpassword"
    }
    response = requests.post(f"{base_url}/managers/", json=manager_data)
    manager = check(response) # 200 OK
    manager_id = manager["id"]
    print(f"Manager created: {manager_id}")
    
    # Verify default rate for manager
    if manager.get("default_rate") == 37.0:
        print("SUCCESS: Manager default_rate is 37.0")
    else:
        print(f"FAILED: Manager default_rate is {manager.get('default_rate')}, expected 37.0")

    # 2. Create a Client (linked to Manager)
    print("\n2. Creating Client...")
    client_data = {
        "client_name": "Shift Corp",
        "mobile": "+1999888777",
        "email": "contact@shiftcorp.com",
        "client_description": "A company needing shifts.",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/clients/", json=client_data)
    client = check(response, 201)
    client_id = client["id"]
    print(f"Client created: {client_id}")

    # 3. Create an Employee (linked to Manager)
    print("\n3. Creating Employee...")
    employee_data = {
        "first_name": "Worker",
        "last_name": "Bee",
        "nickname": "Buzzy",
        "mobile": "+1555666777",
        "email": "worker.bee@example.com",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/employees/", json=employee_data)
    employee = check(response, 201)
    employee_id = employee["id"]
    print(f"Employee created: {employee_id}")

    # Verify default rate for employee
    if employee.get("default_rate") == 0.0:
        print("SUCCESS: Employee default_rate is 0.0")
    else:
        print(f"FAILED: Employee default_rate is {employee.get('default_rate')}, expected 0.0")

    # Verify nickname
    if employee.get("nickname") == "Buzzy":
        print("SUCCESS: Employee nickname is Buzzy")
    else:
        print(f"FAILED: Employee nickname is {employee.get('nickname')}, expected Buzzy")

    # 4. Create a Job Shift
    print("\n4. Creating Job Shift...")
    start_date = datetime.now().isoformat()
    end_date = (datetime.now() + timedelta(hours=8)).isoformat()
    
    shift_data = {
        "manager_id": manager_id,
        "client_id": client_id,
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_paid": False
    }
    
    response = requests.post(f"{base_url}/job_shifts/", json=shift_data)
    shift = check(response, 201)
    shift_id = shift["id"]
    print(f"Job Shift created: {shift_id}")
    
    # 5. List Shifts
    print("\n5. Listing Shifts...")
    response = requests.get(f"{base_url}/job_shifts/")
    shifts = check(response)
    print(f"Found {len(shifts)} shifts")
    
    found = False
    for s in shifts:
        if s["id"] == shift_id:
            found = True
            # Verify details
            if s["manager_id"] != manager_id:
                 print("FAILED: Manager ID mismatch")
            if s["client_id"] != client_id:
                 print("FAILED: Client ID mismatch")
            if s["employee_id"] != employee_id:
                 print("FAILED: Employee ID mismatch")
            break
            
    if not found:
        print("FAILED: Created shift not found in list")
        sys.exit(1)

    print("\nSUCCESS: Job Shifts module verification passed!")

if __name__ == "__main__":
    main()
