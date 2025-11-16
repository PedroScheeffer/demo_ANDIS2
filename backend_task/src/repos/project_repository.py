from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Session, mapped_column, Mapped
from datetime import datetime

from config.database import Base
from models.project import Project, ProjectCreate

class ProjectRepository:

    class _ProjectDB(Base):
        __tablename__ = "projects"

        id: Mapped[int] = mapped_column(primary_key=True, index=True)
        nombre: Mapped[str] = mapped_column(String)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, project_id: int) -> Optional[Project]:
        db_obj = self.db.query(self._ProjectDB).filter(self._ProjectDB.id == project_id).first()
        return self._to_domain(db_obj) if db_obj else None

    def get_by_user_id(self, user_id: int) -> List[Project]:
        db_objs = self.db.query(self._ProjectDB).filter(self._ProjectDB.user_id == user_id).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def create(self, project_data: ProjectCreate, user_id: int) -> Project:
        db_obj = self._ProjectDB(
            nombre=project_data.nombre,
            description=project_data.description,
            user_id=user_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def update(self, project_id: int, project_data: ProjectCreate) -> Optional[Project]:
        db_obj = self.db.query(self._ProjectDB).filter(self._ProjectDB.id == project_id).first()
        if not db_obj:
            return None

        db_obj.nombre = project_data.nombre
        db_obj.description = project_data.description

        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def delete(self, project_id: int) -> bool:
        db_obj = self.db.query(self._ProjectDB).filter(self._ProjectDB.id == project_id).first()
        if not db_obj:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True

    def get_all(self) -> List[Project]:
        db_objs = self.db.query(self._ProjectDB).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def _to_domain(self, db_obj: _ProjectDB) -> Project:
        return Project(
            id=db_obj.id,
            nombre=db_obj.nombre,
            description=db_obj.description,
            user_id=db_obj.user_id,
            created_at=db_obj.created_at
        )