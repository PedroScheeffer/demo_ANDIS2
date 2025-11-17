from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config.database import get_db
from config.jwt import verify_token
from models.user import User

import httpx

# Security scheme for JWT Bearer token
security = HTTPBearer()


async def verify_token_with_auth_service(request: Request) -> dict:
    """
    Verify token by calling the auth service verify endpoint.
    Returns user info if valid.
    """
    AUTH_SERVICE_URL = "http://backend_user:5000/api/auth/verify"

    # Get the Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.post(
                AUTH_SERVICE_URL,
                headers={"authorization": auth_header}
            )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No se pudo contactar al servicio de autenticación"
        )

    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    if response.status_code >= 500:
        raise HTTPException(
            status_code=503,
            detail="El servicio de autenticación respondió con un error interno"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Error verificando token"
        )

    return response.json()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials containing the JWT token
        db: Database session

    Returns:
        User object of the authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify and decode token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_service = UserService(db)
    user = user_service.get_user_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
