from src.database import engine, Base
from src.modules.managers.models import ManagerModel
from src.modules.employees.models import EmployeeModel
from src.modules.clients.models import ClientModel
from src.modules.job_shifts.models import JobShiftModel

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_db()
