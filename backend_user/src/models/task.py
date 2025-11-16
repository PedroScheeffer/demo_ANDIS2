from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Task(BaseModel):
    id: Optional[int] = None
    detalle: str
    project_id: int
    user_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    created_at: Optional[datetime] = None
    completed: bool = False

    def can_have_subtasks(self) -> bool:
        """Business logic for subtask creation"""
        return not self.completed

    def is_subtask(self) -> bool:
        """Check if this task is a subtask"""
        return self.parent_task_id is not None

class TaskCreate(BaseModel):
    detalle: str
    project_id: int
    user_id: Optional[int] = None
    parent_task_id: Optional[int] = None

