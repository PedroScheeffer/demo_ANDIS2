from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib

from models.user import UserCreate
from services.user_service import UserService
from config.database import get_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    id: str
    username: str

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash using the same method as repository"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == hashed

@router.post("/login", response_model=AuthResponse)
def login(
    login_data: LoginRequest,
    service: UserService = Depends(get_user_service)
):
    """Login user with username and password"""
    user = service.get_user_by_nombre(login_data.username)
    if not user or not user.password_hash:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return AuthResponse(
        id=str(user.id),
        username=user.nombre
    )

@router.post("/register", response_model=AuthResponse)
def register(
    register_data: LoginRequest,
    service: UserService = Depends(get_user_service)
):
    """Register new user with username and password"""
    # Check if user already exists
    existing_user = service.get_user_by_nombre(register_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user (password hashing is handled by the repository)
    user_data = UserCreate(
        nombre=register_data.username,
        password=register_data.password
    )

    try:
        user = service.create_user(user_data)
        return AuthResponse(
            id=str(user.id),
            username=user.nombre
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")