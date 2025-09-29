from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.user import UserCreate, UserLogin, Token, User
from services.user_service import UserService
from config.database import get_db
from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/register", response_model=User)
def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    return service.create_user(user_data)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    """Login user and return access token"""
    # Get user by email (OAuth2PasswordRequestForm uses username field for email)
    user = service.get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user with password hash for verification
    from repos.user_repository import UserRepository
    user_repo = UserRepository(service.user_repo.db)
    user_with_hash = user_repo.get_by_email(form_data.username)

    # Verify password
    if not user_with_hash or not user_with_hash.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=Token)
def login_json(
    user_credentials: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """Login user with JSON payload and return access token"""
    # Get user by email
    user = service.get_user_by_email(user_credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user with password hash for verification
    from repos.user_repository import UserRepository
    user_repo = UserRepository(service.user_repo.db)
    user_with_hash = user_repo.get_by_email(user_credentials.email)

    # Verify password
    if not user_with_hash or not user_with_hash.verify_password(user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}