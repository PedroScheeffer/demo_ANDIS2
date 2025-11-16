from typing import Optional, List
from sqlalchemy import DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import Session, mapped_column, Mapped
from datetime import datetime
import httpx

from config.database import Base
from models.task import Task, TaskCreate

class TaskRepository:

    class _TaskDB(Base):
        __tablename__ = "tasks"

        id: Mapped[int] = mapped_column(primary_key=True, index=True)
        detalle: Mapped[str] = mapped_column(Text)
        project_id: Mapped[int] = mapped_column(Integer, index=True)
        user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
        parent_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
        completed: Mapped[bool] = mapped_column(Boolean, default=False)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    PROJECT_SERVICE_URL = "http://backend_project:5000/api/projects"
    USER_SERVICE_URL = "http://backend_user:5000/api/users"

    def __init__(self, db_session: Session):
        self.db = db_session

    # ---- External existence checks ----
    def _project_exists(self, project_id: int) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{self.PROJECT_SERVICE_URL}/{project_id}")
            if resp.status_code == 200:
                return True
            if resp.status_code == 404:
                return False
            return False
        except Exception:
            return False

    def _user_exists(self, user_id: int) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{self.USER_SERVICE_URL}/{user_id}")
            if resp.status_code == 200:
                return True
            if resp.status_code == 404:
                return False
            return False
        except Exception:
            return False

    def get_by_id(self, task_id: int) -> Optional[Task]:
        db_obj = self.db.query(self._TaskDB).filter(self._TaskDB.id == task_id).first()
        return self._to_domain(db_obj) if db_obj else None

    def get_by_project_id(self, project_id: int) -> List[Task]:
        # Validate project existence
        if not self._project_exists(project_id):
            return []
        db_objs = self.db.query(self._TaskDB).filter(self._TaskDB.project_id == project_id).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def get_by_user_id(self, user_id: int) -> List[Task]:
        # Validate user existence
        if not self._user_exists(user_id):
            return []
        db_objs = self.db.query(self._TaskDB).filter(self._TaskDB.user_id == user_id).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def get_subtasks(self, parent_task_id: int) -> List[Task]:
        db_objs = self.db.query(self._TaskDB).filter(self._TaskDB.parent_task_id == parent_task_id).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def create(self, task_data: TaskCreate) -> Task:
        # Validate cross-service references
        if not self._project_exists(task_data.project_id):
            raise ValueError("Proyecto no existe")
        if task_data.user_id is not None and not self._user_exists(task_data.user_id):
            raise ValueError("Usuario asignado no existe")

        db_obj = self._TaskDB(
            detalle=task_data.detalle,
            project_id=task_data.project_id,
            user_id=task_data.user_id,
            parent_task_id=task_data.parent_task_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def update(self, task_id: int, task_data: TaskCreate) -> Optional[Task]:
        db_obj = self.db.query(self._TaskDB).filter(self._TaskDB.id == task_id).first()
        if not db_obj:
            return None

        # Validate cross-service references
        if not self._project_exists(task_data.project_id):
            raise ValueError("Proyecto no existe")
        if task_data.user_id is not None and not self._user_exists(task_data.user_id):
            raise ValueError("Usuario asignado no existe")

        db_obj.detalle = task_data.detalle
        db_obj.project_id = task_data.project_id
        db_obj.user_id = task_data.user_id
        db_obj.parent_task_id = task_data.parent_task_id

        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def mark_completed(self, task_id: int) -> Optional[Task]:
        db_obj = self.db.query(self._TaskDB).filter(self._TaskDB.id == task_id).first()
        if not db_obj:
            return None

        db_obj.completed = True
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def delete(self, task_id: int) -> bool:
        db_obj = self.db.query(self._TaskDB).filter(self._TaskDB.id == task_id).first()
        if not db_obj:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True

    def get_all(self) -> List[Task]:
        db_objs = self.db.query(self._TaskDB).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def _to_domain(self, db_obj: _TaskDB) -> Task:
        return Task(
            id=db_obj.id,
            detalle=db_obj.detalle,
            project_id=db_obj.project_id,
            user_id=db_obj.user_id,
            parent_task_id=db_obj.parent_task_id,
            completed=db_obj.completed,
            created_at=db_obj.created_at
        )