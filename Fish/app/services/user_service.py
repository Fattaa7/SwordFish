import os
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.core.auth.password import hash_password, verify_password
from app.schemas.token_schema import Token
from app.core.auth.jwt import create_access_token
from app.core.config import settings
import requests

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
    
    @staticmethod
    def handle_google_callback(db: Session, code: str) -> Token:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=data)
        if token_response.status_code != 200:
            raise ValueError(f"Failed to obtain tokens: {token_response.text}")

        tokens = token_response.json()
        access_token = tokens.get("access_token")
        if not access_token:
            raise ValueError("Google did not return access_token")

        # ✅ Use userinfo endpoint
        user_info_resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_info_resp.status_code != 200:
            raise ValueError(f"Failed to fetch user info: {user_info_resp.text}")

        user_info = user_info_resp.json()
        email = user_info.get("email")
        if not email:
            raise ValueError("Google account has no email")

        repo = UserRepository(db)
        user = repo.get_by_email(email)
        if not user:
            random_password = os.urandom(16).hex()
            hashed_pw = hash_password(random_password)
            user_data = UserCreate(email=email, password=hashed_pw)
            user = repo.create(user_data)

        access_token = create_access_token(data={"sub": user.email})
        return RedirectResponse(
            url=f"http://localhost:3000/?token={access_token}"
)
    


