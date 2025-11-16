from typing import List, Optional
from sqlalchemy.orm import Session

from models.user import User, UserCreate
from repos.user_repository import UserRepository

class UserService:
    def __init__(self, db_session: Session):
        self.user_repo = UserRepository(db_session)

    def get_all_users(self) -> List[User]:
        """Get all users"""
        users = self.user_repo.get_all()
        return [self._to_response(user) for user in users]

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user = self.user_repo.get_by_id(user_id)
        return self._to_response(user) if user else None

    def get_user_by_nombre(self, nombre: str) -> Optional[User]:
        """Get user by nombre (username)"""
        user = self.user_repo.get_by_nombre(nombre)
        return self._to_response(user) if user else None

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = self.user_repo.create(user_data)
        return self._to_response(user)

    def update_user(self, user_id: int, user_data: UserCreate) -> Optional[User]:
        """Update an existing user"""
        user = self.user_repo.update(user_id, user_data)
        return self._to_response(user) if user else None

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        return self.user_repo.delete(user_id)

    def _to_response(self, user: User) -> User:
        """Convert domain model to response model"""
        return User(
            id=user.id,
            nombre=user.nombre,
            created_at=user.created_at,
            password_hash=user.password_hash
        )