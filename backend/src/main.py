from datetime import datetime
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import init_db, engine, Base
from api.project_router import router as project_router
from api.user_router import router as user_router
from api.task_router import router as task_router
from api.auth_router import router as auth_router
from contextlib import asynccontextmanager
from middleware import (
    CompressionMiddleware,
    RateLimiterMiddleware,
    RequestLoggerMiddleware,
    SecurityHeadersMiddleware
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield

app = FastAPI(title="Gestor de Proyectos API", lifespan=lifespan)
app.router.redirect_slashes = False  # avoid 307 redirects

# CORS middleware (should be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gateway Offloading Pattern - Add middleware in order
# 1. Request Logger - logs all requests
app.add_middleware(RequestLoggerMiddleware)

# 2. Security Headers - adds security headers to all responses
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate Limiter - prevents abuse
app.add_middleware(
    RateLimiterMiddleware,
    requests_per_minute=60,  # 60 requests per minute
    requests_per_hour=1000   # 1000 requests per hour
)

# 4. Compression - compresses responses
app.add_middleware(
    CompressionMiddleware,
    minimum_size=500  # Only compress responses > 500 bytes
)

# Include routers
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

@app.get("/health")
def health_check():
    """Health check endpoint (excluded from rate limiting)"""
    return {"status": "healthy", "pattern": "Gateway Offloading"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, proxy_headers=True, forwarded_allow_ips="*")