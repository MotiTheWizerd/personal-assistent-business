from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from src.modules.job_shifts.models import JobShiftModel
from src.modules.job_shifts.schemas import JobShiftCreate
from uuid import UUID

class JobShiftService:
    def __init__(self, db: Session):
        self.db = db

    def create_shift(self, shift: JobShiftCreate) -> JobShiftModel:
        db_shift = JobShiftModel(
            **shift.model_dump()
        )
        self.db.add(db_shift)
        self.db.commit()
        self.db.refresh(db_shift)
        return db_shift

    def get_shifts(self, skip: int = 0, limit: int = 100) -> list[JobShiftModel]:
        return self.db.query(JobShiftModel).offset(skip).limit(limit).all()

    def get_shifts_by_manager(self, manager_id: UUID, skip: int = 0, limit: int = 100) -> list[JobShiftModel]:
        return self.db.query(JobShiftModel).filter(JobShiftModel.manager_id == manager_id).offset(skip).limit(limit).all()

    def get_shifts_by_params(
        self, 
        manager_id: UUID, 
        employee_id: UUID = None, 
        client_id: UUID = None, 
        start_date: datetime = None, 
        end_date: datetime = None
    ) -> list[JobShiftModel]:
        from datetime import timedelta
        
        # Default date logic
        if not start_date or not end_date:
            now = datetime.now()
            # Set to start of today to include shifts that already started today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=30)
            
        query = self.db.query(JobShiftModel).filter(
            JobShiftModel.manager_id == manager_id,
            JobShiftModel.start_date >= start_date,
            JobShiftModel.start_date <= end_date
        )
        
        if employee_id:
            query = query.filter(JobShiftModel.employee_id == employee_id)
        if client_id:
            query = query.filter(JobShiftModel.client_id == client_id)
            
        return query.all()

    def get_schedule_by_params(
        self,
        manager_id: UUID = None,
        employee_id: UUID = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> list[JobShiftModel]:
        query = self.db.query(JobShiftModel).options(
            joinedload(JobShiftModel.client),
            joinedload(JobShiftModel.employee)
        )

        if manager_id:
            query = query.filter(JobShiftModel.manager_id == manager_id)
        if employee_id:
            query = query.filter(JobShiftModel.employee_id == employee_id)

        if start_date and end_date:
            query = query.filter(
                JobShiftModel.start_date >= start_date,
                JobShiftModel.start_date <= end_date
            )
        elif start_date:
            query = query.filter(JobShiftModel.start_date >= start_date)
        elif end_date:
            query = query.filter(JobShiftModel.start_date <= end_date)

        return query.all()
