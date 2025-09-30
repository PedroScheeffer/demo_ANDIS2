from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.task import TaskCreate, Task
from models.user import User
from services.task_service import TaskService
from config.database import get_db
from config.auth_dependency import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)

@router.get("/", response_model=List[Task])
def get_tasks(
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Listar todas las tareas"""
    return service.get_all_tasks()

@router.post("/", response_model=Task)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Crear una nueva tarea"""
    return service.create_task(task)

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Obtener una tarea específica"""
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Actualizar una tarea"""
    updated_task = service.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return updated_task

@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Marcar una tarea como completada"""
    completed_task = service.mark_task_completed(task_id)
    if not completed_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return completed_task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Eliminar una tarea"""
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": "Tarea eliminada exitosamente"}

@router.get("/project/{project_id}", response_model=List[Task])
def get_tasks_by_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Obtener todas las tareas de un proyecto"""
    return service.get_tasks_by_project(project_id)

@router.get("/user/{user_id}", response_model=List[Task])
def get_tasks_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Obtener todas las tareas asignadas a un usuario"""
    return service.get_tasks_by_user(user_id)

@router.get("/{task_id}/subtasks", response_model=List[Task])
def get_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Obtener todas las subtareas de una tarea"""
    return service.get_subtasks(task_id)

@router.post("/{parent_task_id}/subtasks", response_model=Task)
def create_subtask(
    parent_task_id: int,
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Crear una subtarea"""
    subtask = service.create_subtask(parent_task_id, task)
    if not subtask:
        raise HTTPException(
            status_code=400,
            detail="No se puede crear subtarea. La tarea padre no permite subtareas o no existe"
        )
    return subtask