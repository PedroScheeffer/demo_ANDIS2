from typing import Optional, List
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Session, mapped_column, Mapped
from datetime import datetime

from config.database import Base
from models.user import User, UserCreate

class UserRepository:

    class _UserDB(Base):
        __tablename__ = "users"

        id: Mapped[int] = mapped_column(primary_key=True, index=True)
        nombre: Mapped[str] = mapped_column(String, unique=True, index=True)
        password_hash: Mapped[str] = mapped_column(String)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, user_id: int) -> Optional[User]:
        db_obj = self.db.query(self._UserDB).filter(self._UserDB.id == user_id).first()
        return self._to_domain(db_obj) if db_obj else None

    def get_by_nombre(self, nombre: str) -> Optional[User]:
        db_obj = self.db.query(self._UserDB).filter(self._UserDB.nombre == nombre).first()
        return self._to_domain(db_obj) if db_obj else None

    def create(self, user_data: UserCreate) -> User:
        import hashlib
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        db_obj = self._UserDB(
            nombre=user_data.nombre,
            password_hash=password_hash
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def update(self, user_id: int, user_data: UserCreate) -> Optional[User]:
        db_obj = self.db.query(self._UserDB).filter(self._UserDB.id == user_id).first()
        if not db_obj:
            return None

        db_obj.nombre = user_data.nombre
        if user_data.password:
            import hashlib
            db_obj.password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    def delete(self, user_id: int) -> bool:
        db_obj = self.db.query(self._UserDB).filter(self._UserDB.id == user_id).first()
        if not db_obj:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True

    def get_all(self) -> List[User]:
        db_objs = self.db.query(self._UserDB).all()
        return [self._to_domain(db_obj) for db_obj in db_objs]

    def _to_domain(self, db_obj: _UserDB) -> User:
        return User(
            id=db_obj.id,
            nombre=db_obj.nombre,
            password_hash=db_obj.password_hash,
            created_at=db_obj.created_at
        )