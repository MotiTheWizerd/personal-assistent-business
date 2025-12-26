from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.modules.job_shifts.models import JobShiftModel
# Need to import these to satisfy relationships
from src.modules.managers.models import ManagerModel
from src.modules.employees.models import EmployeeModel
from src.modules.clients.models import ClientModel
from uuid import UUID
from datetime import datetime

import sys

def debug_shifts(manager_id_str):
    db = SessionLocal()
    try:
        manager_id = UUID(manager_id_str)
        shifts = db.query(JobShiftModel).filter(JobShiftModel.manager_id == manager_id).all()
        print(f"Total shifts for manager {manager_id_str}: {len(shifts)}")
        for s in shifts:
            print(f"Shift ID: {s.id}")
            print(f"  Start: {s.start_date}")
            print(f"  End:   {s.end_date}")
            print(f"  Employee: {s.employee_id}")
            print("-" * 20)
        
        now = datetime.now()
        print(f"\nCurrent time (now): {now}")
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_shifts(sys.argv[1])
    else:
        # User's manager_id from message
        debug_shifts("fc8809b3-660b-4a7a-9204-2ef7336e1cb0")
