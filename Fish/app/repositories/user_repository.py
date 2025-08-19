from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, create: UserCreate) -> UserResponse: 
        user = User(
            email=create.email,
            hashed_password=create.password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
