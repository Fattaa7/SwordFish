from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.core.auth.password import hash_password, verify_password
from app.schemas.token_schema import Token
from app.core.auth.jwt import create_access_token

class UserService:
    @staticmethod
    def register_user(db: Session, email: str, password: str):
        repo = UserRepository(db)

        # Check if user already exists
        existing_user = repo.get_by_email(email)
        if existing_user:
            raise ValueError("User already exists")

        # Hash the password
        hashed_pw = hash_password(password)
        
        # Create user data object
        user_data = UserCreate(email=email, password=hashed_pw)
        
        # Create user via repository
        return repo.create(user_data)

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> Token:
        repo = UserRepository(db)
        user = repo.get_by_email(email)
        
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.email})
        token = Token(access_token=access_token, token_type="bearer")
        return token

    @staticmethod
    def get_user(db: Session, user_id: int):
        repo = UserRepository(db)
        user = repo.get_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        return user