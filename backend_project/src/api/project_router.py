from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.user import User
from models.project import ProjectCreate, Project
from services.project_service import ProjectService
from config.database import get_db
from config.auth_dependency import get_current_user

# Usamos httpx para llamar al microservicio de usuarios
import httpx

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
def get_projects(
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Listar proyectos del usuario autenticado"""
    return service.get_projects_by_user(current_user.id)


@router.post("/", response_model=Project)
@router.post("", response_model=Project, include_in_schema=False)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Crear un nuevo proyecto"""

    # ==========================================================
    # 🔍 VALIDACIÓN NUEVA (TFU5):
    # Antes de crear un proyecto, consultamos al microservicio
    # USERS para verificar que el usuario realmente exista.
    #
    # Esto reemplaza la integridad referencial (foreign key)
    # que antes garantizaba la base en el monolito.
    # ==========================================================

    USER_SERVICE_URL = "http://backend_user:5000/api/users"

    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(f"{USER_SERVICE_URL}/{current_user.id}")
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No se pudo contactar al servicio de usuarios"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=400,
            detail="El usuario propietario no existe en el servicio USERS"
        )

    if response.status_code >= 500:
        raise HTTPException(
            status_code=503,
            detail="El servicio USERS respondió con un error interno"
        )

    # ==========================================================
    # ✔️ Usuario EXISTE → continuar con la creación normal
    # ==========================================================

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

    # Validar propiedad
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para acceder a este proyecto"
        )

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

    # Validar propiedad
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para eliminar este proyecto"
        )

    if not service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return {"message": "Proyecto eliminado exitosamente"}
