from datetime import datetime
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import init_db
from api.project_router import router as project_router
from api.user_router import router as user_router
from api.task_router import router as task_router
from api.auth_router import router as auth_router


from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield

app = FastAPI(title="Gestor de Proyectos API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from repos import user_repository, task_repository, project_repository  # type: ignore Import to register all models
app.include_router(project_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(auth_router)

@app.get("/")
def read_root() -> dict[str, Any]:
    return {
        "message": "Gestor de Proyectos API. en /docs tienen swagger para probar la api",
        "version": "1.0.0",
        "endpoints": {
            "projects": "/api/projects",
            "users": "/api/users",
            "tasks": "/api/tasks",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)