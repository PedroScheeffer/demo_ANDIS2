import os
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

from config.database import get_db
from services.user_service import UserService
from models.user import UserCreate
from config.jwt import create_access_token

router = APIRouter()

# en api/auth_google.py, justo antes de oauth.register(...)
print("GOOGLE_ID:", os.getenv('GOOGLE_CLIENT_ID'))
print("GOOGLE_SECRET_LAST6:", (os.getenv('GOOGLE_CLIENT_SECRET') or "")[-6:])


oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get('/auth/google')
async def login_via_google(request: Request):
    redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
    print("Redirect URI ENVIADA A GOOGLE:", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/auth/google/callback')
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("TOKEN OK:", token)
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=400)

    user_info = token.get('userinfo') or {}
    email = user_info.get('email')
    picture = user_info.get('picture')
    name = user_info.get('name')

    if not email:
        raise HTTPException(status_code=400, detail="Google did not return an email")

    # Buscar o crear usuario
    service = UserService(db)
    user = service.get_user_by_nombre(email)
    if not user:
        user = service.create_user(UserCreate(
            nombre=email,
            password="__google_oauth__"
        ))

    # Emitir JWT propio
    access_token = create_access_token(data={"sub": str(user.id), "username": user.nombre})

    from fastapi.responses import RedirectResponse, JSONResponse

    redirect_url = f"https://app.facumar93.win/auth/callback#access_token={access_token}&username={user.nombre}&id={user.id}&picture={picture}"
    print("Redirigiendo a:", redirect_url)
    return RedirectResponse(url=redirect_url)

    # (solo para pruebas, no se ejecutará)
    return JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.nombre,
            "display_name": name,
            "picture": picture
        }
    })

