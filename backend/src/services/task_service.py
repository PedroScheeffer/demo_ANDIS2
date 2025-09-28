from typing import List, Optional
from sqlalchemy.orm import Session

from models.task import Task, TaskCreate
from repos.task_repository import TaskRepository

class TaskService:
    def __init__(self, db_session: Session):
        self.task_repo = TaskRepository(db_session)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        tasks = self.task_repo.get_all()
        return [self._to_response(task) for task in tasks]

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        task = self.task_repo.get_by_id(task_id)
        return self._to_response(task) if task else None

    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task = self.task_repo.create(task_data)
        return self._to_response(task)

    def update_task(self, task_id: int, task_data: TaskCreate) -> Optional[Task]:
        """Update an existing task"""
        task = self.task_repo.update(task_id, task_data)
        return self._to_response(task) if task else None

    def mark_task_completed(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed"""
        task = self.task_repo.mark_completed(task_id)
        return self._to_response(task) if task else None

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        return self.task_repo.delete(task_id)

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Get all tasks for a specific project"""
        tasks = self.task_repo.get_by_project_id(project_id)
        return [self._to_response(task) for task in tasks]

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """Get all tasks assigned to a specific user"""
        tasks = self.task_repo.get_by_user_id(user_id)
        return [self._to_response(task) for task in tasks]

    def get_subtasks(self, parent_task_id: int) -> List[Task]:
        """Get all subtasks of a parent task"""
        tasks = self.task_repo.get_subtasks(parent_task_id)
        return [self._to_response(task) for task in tasks]

    def create_subtask(self, parent_task_id: int, task_data: TaskCreate) -> Optional[Task]:
        """Create a subtask for an existing task"""
        # Check if parent task can have subtasks
        parent_task = self.task_repo.get_by_id(parent_task_id)
        if not parent_task or not parent_task.can_have_subtasks():
            return None

        # Set the parent task ID
        task_data.parent_task_id = parent_task_id
        task = self.task_repo.create(task_data)
        return self._to_response(task)

    def _to_response(self, task: Task) -> Task:
        """Convert domain model to response model"""
        return Task(
            id=task.id,
            detalle=task.detalle,
            project_id=task.project_id,
            user_id=task.user_id,
            parent_task_id=task.parent_task_id,
            created_at=task.created_at,
            completed=task.completed
        )