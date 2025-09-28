from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Project(BaseModel):
    id: Optional[int] = None
    nombre: str
    description: Optional[str] = None
    user_id: int
    created_at: Optional[datetime] = None

    def can_be_deleted(self) -> bool:
        """Business logic for project deletion"""
        return True

class ProjectCreate(BaseModel):
    nombre: str
    description: Optional[str] = None
