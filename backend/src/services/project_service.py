from typing import List, Optional
from sqlalchemy.orm import Session
import json
from config.redis_client import redis_client
from config.redis_utils import enqueue_project_task

from models.project import Project, ProjectCreate
from repos.project_repository import ProjectRepository

class ProjectService:
    CACHE_KEY = "projects:all"
    CACHE_TTL = 300 #5 min
    
    def __init__(self, db_session: Session):
        self.project_repo = ProjectRepository(db_session)
        
    def delete_cache(self):
        redis_client.delete(self.CACHE_KEY)

    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        projects = self.project_repo.get_all()
        return [self._to_response(project) for project in projects]

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        project = self.project_repo.get_by_id(project_id)
        return self._to_response(project) if project else None


    def create_project(self, project_data: ProjectCreate, user_id: int):
        enqueue_project_task(project_data, user_id)
        return {"message": "Project creation enqueued."}


    # def create_project(self, project_data: ProjectCreate, user_id: int) -> Project:
    #     """Create a new project"""
    #     project = self.project_repo.create(project_data, user_id)
    #     self.delete_cache()
    #     return self._to_response(project)

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        project = self.project_repo.get_by_id(project_id)
        self.delete_cache()
        if project and project.can_be_deleted():
            return self.project_repo.delete(project_id)
        return False

    def get_projects_by_user(self, user_id: int) -> List[Project]:
        """Get all projects for a specific user"""
        cached_projects = redis_client.get(self.CACHE_KEY)
        if cached_projects:
            print("Cache hit")
            return json.loads(cached_projects)

        print("💾 Cache miss — querying DB")
        projects = self.project_repo.get_by_user_id(user_id)
        response = [self._to_response(p) for p in projects]

        redis_client.setex(self.CACHE_KEY, self.CACHE_TTL, json.dumps(response))

        return response

    def _to_response(self, project: Project) -> Project:
        """Convert domain model to response model"""
        return Project(
            id=project.id,
            nombre=project.nombre,
            description=project.description,
            user_id=project.user_id,
            created_at=project.created_at
        )