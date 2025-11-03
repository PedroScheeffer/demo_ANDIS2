from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from patterns.bulkhead import BulkheadException
import logging

logger = logging.getLogger(__name__)

@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    try:
        logger.info("GET /projects - Starting request")
        service = ProjectService(db)
        result = service.get_all_projects()
        logger.info("GET /projects - Completed successfully")
        return result
    except BulkheadException as e:
        logger.warning(f"GET /projects - Bulkhead limit exceeded: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"Service temporarily unavailable: {str(e)}"
        )

@router.post("/projects")
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    try:
        logger.info("POST /projects - Starting request")
        service = ProjectService(db)
        result = service.create_project(project_data, user_id)
        logger.info("POST /projects - Completed successfully")
        return result
    except BulkheadException as e:
        logger.warning(f"POST /projects - Bulkhead limit exceeded: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable: {str(e)}"
        )