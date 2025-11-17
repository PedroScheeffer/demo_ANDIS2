from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from sqlalchemy.orm import Session

from models.project import ProjectCreate, Project
from services.project_service import ProjectService
from config.database import get_db
from config.auth_dependency import verify_token_with_auth_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


"""
Project endpoints

El router contiene los endpoints. Es la capa donde se validan
precondiciones externas (como verificar que un usuario exista)
antes de delegar la lógica al service.
"""


@router.get("/", response_model=List[Project])
@router.get("", response_model=List[Project], include_in_schema=False)
async def get_projects(
    request: Request,
    service: ProjectService = Depends(get_project_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Listar proyectos del usuario autenticado"""
    return service.get_projects_by_user(int(auth_verify["user_id"]))


@router.post("/", response_model=Project)
@router.post("", response_model=Project, include_in_schema=False)
async def create_project(
    project: ProjectCreate,
    request: Request,
    service: ProjectService = Depends(get_project_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Crear un nuevo proyecto"""

    # ==========================================================
    # ✔️ Token VERIFICADO con servicio de autenticación
    # El usuario es auténtico y su token es válido.
    # Continuamos con la creación del proyecto.
    # ==========================================================

    return service.create_project(project, int(auth_verify["user_id"]))


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    request: Request,
    service: ProjectService = Depends(get_project_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Obtener un proyecto específico"""
    user_id = int(auth_verify["user_id"])
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Validar propiedad
    if project.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para acceder a este proyecto"
        )

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    request: Request,
    service: ProjectService = Depends(get_project_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Eliminar un proyecto"""
    user_id = int(auth_verify["user_id"])
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Validar propiedad
    if project.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para eliminar este proyecto"
        )

    if not service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return {"message": "Proyecto eliminado exitosamente"}
