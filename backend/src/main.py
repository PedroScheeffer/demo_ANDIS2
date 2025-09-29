from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette import status
from contextlib import asynccontextmanager

import asyncio
import os
import socket
import time
from collections import deque, defaultdict

from config.database import init_db
from api.project_router import router as project_router
from api.user_router import router as user_router
from api.task_router import router as task_router
from api.auth_router import router as auth_router  # <-- auth de Pedro

# Import para registrar modelos (como tenías)
from repos import user_repository, task_repository, project_repository  # type: ignore  # noqa: F401

# -----------------------------
# App & Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    import os
    if os.getenv("INIT_DB") == "1":
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

# -----------------------------
# Middlewares
# -----------------------------

# 1) Rechazar GET con body -> 400
@app.middleware("http")
async def reject_get_with_body(request: Request, call_next):
    if request.method == "GET":
        content_length = request.headers.get("content-length")
        transfer_encoding = request.headers.get("transfer-encoding", "").lower()
        has_body = False
        try:
            if content_length is not None and int(content_length) > 0:
                has_body = True
        except ValueError:
            # Si el header es inválido, lo tratamos como potencial cuerpo
            has_body = True
        if "chunked" in transfer_encoding:
            has_body = True

        if has_body:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "GET requests must not include a body."},
            )
    return await call_next(request)

# 2) Rate limiting simple en memoria: 10 req / 10 s por IP -> 429
_RATE_LIMIT = 10
_RATE_WINDOW_SECONDS = 10.0
_access_log: Dict[str, deque] = defaultdict(deque)  # ip -> deque[timestamps]
_access_lock = asyncio.Lock()

@app.middleware("http")
async def rate_limit_per_ip(request: Request, call_next):
    client_ip = (request.client.host if request.client else "unknown") or "unknown"
    now = time.monotonic()
    cutoff = now - _RATE_WINDOW_SECONDS

    async with _access_lock:
        dq = _access_log[client_ip]
        # Limpiar timestamps fuera de ventana
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= _RATE_LIMIT:
            retry_after = max(1, int(_RATE_WINDOW_SECONDS))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(retry_after)},
                content={"detail": "Too Many Requests"},
            )
        dq.append(now)

    return await call_next(request)

# 3) API Key simple en header -> 401 si no coincide
API_KEY = os.getenv("API_KEY")  # si no se define, queda desactivado

@app.middleware("http")
async def require_api_key(request: Request, call_next):
    # Solo exigir si hay API_KEY configurada
    if API_KEY:
        # Endpoints públicos permitidos sin API Key
        public_paths = ["/health", "/whoami", "/docs", "/redoc", "/openapi.json", "/"]
        path = request.url.path
        if (path not in public_paths) and (not path.startswith("/api/auth")):
            key = request.headers.get("X-API-Key")
            if key != API_KEY:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or missing API Key."},
                )
    return await call_next(request)

# -----------------------------
# Routers
# -----------------------------
# auth de Pedro (su router ya debería tener prefix="/api/auth")
app.include_router(auth_router)

app.include_router(project_router)
app.include_router(user_router)
app.include_router(task_router)

# -----------------------------
# Endpoints utilitarios
# -----------------------------
@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/whoami")
async def whoami() -> Dict[str, str]:
    hostname = socket.gethostname()
    service = os.getenv("SERVICE_NAME", "")
    label = service or hostname
    return {
        "service": label,
        "hostname": hostname,
        "message": "You are hitting this specific instance.",
    }

@app.get("/")
def read_root() -> Dict[str, Any]:
    return {
        "message": "Gestor de Proyectos API. En /docs tienen Swagger para probar la API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "projects": "/api/projects",
            "users": "/api/users",
            "tasks": "/api/tasks",
            "health": "/health",
            "whoami": "/whoami",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
