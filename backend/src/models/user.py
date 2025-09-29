from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    id: Optional[int] = None
    nombre: str
    email: str
    password_hash: str | None = None
    created_at: Optional[datetime] = None

    def can_create_project(self) -> bool:
        """Business logic for user permissions"""
        return True

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        if not self.password_hash:
            return False
        return pwd_context.verify(password, self.password_hash)

class UserCreate(BaseModel):
    nombre: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
