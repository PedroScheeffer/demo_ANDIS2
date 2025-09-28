from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.project import ProjectCreate, Project
from services.project_service import ProjectService
from config.database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.get("/", response_model=List[Project])
def get_projects(service: ProjectService = Depends(get_project_service)):
    """Listar todos los proyectos"""
    return service.get_all_projects()

@router.post("/", response_model=Project)
def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
):
    """Crear un nuevo proyecto"""
    return service.create_project(project)

@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    """Obtener un proyecto específico"""
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    """Eliminar un proyecto"""
    if not service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"message": "Proyecto eliminado exitosamente"}

@router.get("/user/{user_id}", response_model=List[Project])
def get_projects_by_user(
    user_id: int,
    service: ProjectService = Depends(get_project_service)
):
    """Obtener todos los proyectos de un usuario"""
    return service.get_projects_by_user(user_id)