from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import urllib.parse
from app.models.user import User
from app.core.dependencies import get_current_user, get_db
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.token_schema import Token
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return UserService.register_user(db, user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        access_token = UserService.login_user(db, form_data.username, form_data.password)
        return access_token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    
@router.get("/auth/callback", response_model=Token)
def google_callback(code: str, state: str = None, db: Session = Depends(get_db)):
    """
    Thin controller: just hands off to the service layer.
    """
    try:
        return UserService.handle_google_callback(db, code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/google/login")
def login_with_google():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",  # for refresh_token support
        "prompt": "consent",       # force account picker
        "state": "random_string",  # TODO: generate a real random state for CSRF protection
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

