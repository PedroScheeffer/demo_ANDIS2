from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from sqlalchemy.orm import Session

from models.task import TaskCreate, Task
from services.task_service import TaskService
from config.database import get_db
from config.auth_dependency import verify_token_with_auth_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


"""Task endpoints (root accepts both with/without trailing slash).
See project_router for rationale.
"""


@router.get("/", response_model=List[Task])
@router.get("", response_model=List[Task], include_in_schema=False)
async def get_tasks(
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Listar todas las tareas"""
    return service.get_all_tasks()


@router.post("/", response_model=Task)
@router.post("", response_model=Task, include_in_schema=False)
async def create_task(
    task: TaskCreate,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Crear una nueva tarea"""
    try:
        return service.create_task(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Obtener una tarea específica"""
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task: TaskCreate,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Actualizar una tarea"""
    try:
        updated_task = service.update_task(task_id, task)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: int,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Marcar una tarea como completada"""
    completed_task = service.mark_task_completed(task_id)
    if not completed_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return completed_task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Eliminar una tarea"""
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": "Tarea eliminada exitosamente"}


@router.get("/project/{project_id}", response_model=List[Task])
async def get_tasks_by_project(
    project_id: int,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Obtener todas las tareas de un proyecto"""
    return service.get_tasks_by_project(project_id)


@router.get("/user/{user_id}", response_model=List[Task])
async def get_tasks_by_user(
    user_id: int,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Obtener todas las tareas asignadas a un usuario"""
    return service.get_tasks_by_user(user_id)


@router.get("/{task_id}/subtasks", response_model=List[Task])
async def get_subtasks(
    task_id: int,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Obtener todas las subtareas de una tarea"""
    return service.get_subtasks(task_id)


@router.post("/{parent_task_id}/subtasks", response_model=Task)
async def create_subtask(
    parent_task_id: int,
    task: TaskCreate,
    request: Request,
    service: TaskService = Depends(get_task_service),
    auth_verify: dict = Depends(verify_token_with_auth_service)
):
    """Crear una subtarea"""
    try:
        subtask = service.create_subtask(parent_task_id, task)
        if not subtask:
            raise HTTPException(
                status_code=400,
                detail="No se puede crear subtarea. La tarea padre no permite subtareas o no existe"
            )
        return subtask
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
