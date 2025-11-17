from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    nombre: str
    password_hash: str 
    created_at: Optional[datetime] = None

    def can_create_project(self) -> bool:
        """Business logic for user permissions"""
        return True

class UserCreate(BaseModel):
    nombre: str
    password: str
