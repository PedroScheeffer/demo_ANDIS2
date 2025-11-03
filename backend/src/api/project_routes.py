from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from patterns.bulkhead import BulkheadException

# Add this to your existing route handlers

@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    try:
        service = ProjectService(db)
        return service.get_all_projects()
    except BulkheadException as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service temporarily unavailable: {str(e)}"
        )

@router.post("/projects")
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    try:
        service = ProjectService(db)
        return service.create_project(project_data, user_id)
    except BulkheadException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable: {str(e)}"
        )