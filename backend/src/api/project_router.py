from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.user import User
from models.project import ProjectCreate, Project
from services.project_service import ProjectService
from config.database import get_db
from config.auth_dependency import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


"""Project endpoints.

We expose both trailing and non-trailing slash variants because the main app
has redirect_slashes = False. Without this, calling /api/projects (no slash)
would return 404 even though /api/projects/ exists. By stacking two decorators
we accept both forms without a 307 redirect that previously downgraded scheme.
"""


@router.get("/", response_model=List[Project])
@router.get("", response_model=List[Project], include_in_schema=False)
def get_projects(
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Listar todos los proyectos del usuario autenticado"""
    return service.get_projects_by_user(current_user.id)


@router.post("/", response_model=Project)
@router.post("", response_model=Project, include_in_schema=False)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Crear un nuevo proyecto"""
    return service.create_project(project, current_user.id)


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Obtener un proyecto específico"""
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Verify user owns the project
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para acceder a este proyecto")

    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Eliminar un proyecto"""
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Verify user owns the project
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para eliminar este proyecto")

    if not service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"message": "Proyecto eliminado exitosamente"}
