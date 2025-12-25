from sqlalchemy.orm import Session
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
