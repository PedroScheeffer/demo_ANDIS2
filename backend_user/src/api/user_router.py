from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.user import UserCreate, User
from services.user_service import UserService
from config.database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


"""User endpoints (root accepts both with/without trailing slash).
Redirects disabled at app level, so expose both to avoid 404.
"""


@router.get("/", response_model=List[User])
@router.get("", response_model=List[User], include_in_schema=False)
def get_users(service: UserService = Depends(get_user_service)):
    """Listar todos los usuarios"""
    return service.get_all_users()


@router.post("/", response_model=User)
@router.post("", response_model=User, include_in_schema=False)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Crear un nuevo usuario"""
    return service.create_user(user)


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """Obtener un usuario específico"""
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Actualizar un usuario"""
    updated_user = service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return updated_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """Eliminar un usuario"""
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado exitosamente"}
