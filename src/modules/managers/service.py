from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.modules.managers.models import ManagerModel
from src.modules.managers.schemas import ManagerCreate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class ManagerService:
    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_manager(self, manager: ManagerCreate):
        hashed_password = self.get_password_hash(manager.password)
        db_manager = ManagerModel(
            first_name=manager.first_name,
            last_name=manager.last_name,
            username=manager.username,
            email=manager.email,
            password=hashed_password
        )
        self.db.add(db_manager)
        self.db.commit()
        self.db.refresh(db_manager)
        return db_manager

    def get_managers(self, skip: int = 0, limit: int = 100):
        return self.db.query(ManagerModel).offset(skip).limit(limit).all()

    def get_manager_by_email(self, email: str):
        return self.db.query(ManagerModel).filter(ManagerModel.email == email).first()

    def authenticate_manager(self, email: str, password: str):
        manager = self.get_manager_by_email(email=email)
        if not manager:
            return None
        if not self.verify_password(password, manager.password):
            return None
        return manager
