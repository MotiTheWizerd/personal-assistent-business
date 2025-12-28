import sys
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ensure src is in pythonpath
sys.path.append(os.getcwd())
load_dotenv()

from src.database import SessionLocal
from src.modules.managers.models import ManagerModel
from src.modules.employees.models import EmployeeModel
from src.modules.clients.models import ClientModel
from src.modules.job_shifts.models import JobShiftModel
from src.modules.agents.models import AgentModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- Mock Data ---
MOCK_NAMES = [
    ("James", "Smith"), ("Mary", "Johnson"), ("Robert", "Williams"), ("Patricia", "Brown"),
    ("John", "Jones"), ("Jennifer", "Garcia"), ("Michael", "Miller"), ("Linda", "Davis"),
    ("David", "Rodriguez"), ("Elizabeth", "Martinez"), ("William", "Hernandez"), ("Barbara", "Lopez"),
    ("Richard", "Gonzalez"), ("Susan", "Wilson"), ("Joseph", "Anderson"), ("Jessica", "Thomas"),
    ("Thomas", "Taylor"), ("Sarah", "Moore"), ("Charles", "Jackson"), ("Karen", "Martin")
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    return pwd_context.hash(password)

def seed_db():
    print("--- Robust Database Seeder (Direct DB Access) ---")
    db = SessionLocal()
    
    try:
        # 1. Select Random Identities
        random.shuffle(MOCK_NAMES)
        manager_identity = MOCK_NAMES[0]
        employee_identities = MOCK_NAMES[1:4] # Pick next 3
        
        # 2. Require/Create 1 Manager
        manager_email = f"{manager_identity[0].lower()}.{manager_identity[1].lower()}@example.com"
        manager = db.query(ManagerModel).filter(ManagerModel.email == manager_email).first()
        
        if not manager:
            print(f"Creating Manager: {manager_identity[0]} {manager_identity[1]} ({manager_email})")
            manager = ManagerModel(
                first_name=manager_identity[0],
                last_name=manager_identity[1],
                username=f"{manager_identity[0].lower()}_{manager_identity[1].lower()}",
                email=manager_email,
                password=hash_password("password123")
            )
            db.add(manager)
            db.commit()
            db.refresh(manager)
        else:
            print(f"Manager already exists: {manager.email}")
            
        # 3. Require/Create 1 Client (linked to manager)
        client_name = "Seed Corp"
        client = db.query(ClientModel).filter(ClientModel.email == "contact@seedcorp.com").first()
        
        if not client:
            print(f"Creating Client: {client_name}")
            client = ClientModel(
                client_name=client_name,
                mobile="+1555999888",
                email="contact@seedcorp.com",
                client_description="Primary seed client",
                manager_id=manager.id
            )
            db.add(client)
            db.commit()
            db.refresh(client)
        else:
             print(f"Client already exists: {client.client_name}")

        # 4. Require/Create 3 Employees
        employees = []
        for first, last in employee_identities:
            email = f"{first.lower()}.{last.lower()}@example.com"
            emp = db.query(EmployeeModel).filter(EmployeeModel.email == email).first()
            
            if not emp:
                print(f"Creating Employee: {first} {last} ({email})")
                emp = EmployeeModel(
                    first_name=first,
                    last_name=last,
                    nickname=first[:3],
                    mobile=f"+1555{random.randint(1000,9999)}",
                    email=email,
                    manager_id=manager.id
                )
                db.add(emp)
                db.commit()
                db.refresh(emp)
            else:
                 print(f"Employee already exists: {email}")
            employees.append(emp)
            
        # 5. Create 4 Random Job Shifts
        # We always create new shifts for this run, or check if similar ones exist? 
        # User said "seed 4 shifts". Let's simply create 4 new ones to ensure data presence.
        print("Creating 4 Random Job Shifts...")
        now = datetime.now()
        
        for i in range(4):
            emp = random.choice(employees)
            
            # Randomize start day (next 7 days) and time (8am-4pm)
            days_offset = random.randint(1, 7)
            hour_offset = random.randint(8, 16)
            
            start_time = now + timedelta(days=days_offset)
            start_time = start_time.replace(hour=hour_offset, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=8)
            
            shift = JobShiftModel(
                manager_id=manager.id,
                client_id=client.id,
                employee_id=emp.id,
                start_date=start_time,
                end_date=end_time,
                is_paid=False
            )
            db.add(shift)
            print(f"   Shift created for {emp.first_name}: {start_time.strftime('%Y-%m-%d %H:%M')}")
            
        db.commit()
        print("\nSeeding Complete Successfully.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
