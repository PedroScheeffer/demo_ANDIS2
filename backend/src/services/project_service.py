from typing import List, Optional
from sqlalchemy.orm import Session

from models.project import Project, ProjectCreate
from repos.project_repository import ProjectRepository

class ProjectService:
    def __init__(self, db_session: Session):
        self.project_repo = ProjectRepository(db_session)

    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        projects = self.project_repo.get_all()
        return [self._to_response(project) for project in projects]

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        project = self.project_repo.get_by_id(project_id)
        return self._to_response(project) if project else None

    def create_project(self, project_data: ProjectCreate, user_id: int = 1) -> Project:
        """Create a new project"""
        project = self.project_repo.create(project_data, user_id)
        return self._to_response(project)

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        project = self.project_repo.get_by_id(project_id)
        if project and project.can_be_deleted():
            return self.project_repo.delete(project_id)
        return False

    def get_projects_by_user(self, user_id: int) -> List[Project]:
        """Get all projects for a specific user"""
        projects = self.project_repo.get_by_user_id(user_id)
        return [self._to_response(project) for project in projects]

    def _to_response(self, project: Project) -> Project:
        """Convert domain model to response model"""
        return Project(
            id=project.id,
            nombre=project.nombre,
            description=project.description,
            user_id=project.user_id,
            created_at=project.created_at
        )