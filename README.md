## Variables de entorno

### Backend (FastAPI)
- **POSTGRES_HOST**: host de la base de datos (por ejemplo `db` en Docker o el servicio en Coolify).  
- **POSTGRES_PORT**: puerto del servicio PostgreSQL (`5432` por defecto).  
- **POSTGRES_DB**: nombre de la base de datos.  
- **POSTGRES_USER**: usuario de la base de datos.  
- **POSTGRES_PASSWORD**: contraseña del usuario de base de datos.  
- **JWT_SECRET**: clave para firmar tokens JWT.  
- **ALLOWED_ORIGINS**: lista de orígenes permitidos para CORS (por ejemplo `["https://app.localtest.me"]`).  

### Frontend (Svelte)
- **VITE_API_BASE_URL**: URL pública/base del backend FastAPI (por ejemplo `https://api.localtest.me`).  

---

## Puertos y servicios
- **Backend**: 8000  
- **Frontend**: 5173 (dev) / 80 (prod)  
- **Base de datos (Postgres)**: 5432  
- **Traefik / Proxy reverso**: 80 y 443  

---

## Despliegue en Coolify
- **Backend** → `backend/Dockerfile`  
  - Copia el código de FastAPI  
  - Expone el puerto 8000  
  - Arranca con `uvicorn`  
- **Frontend** → `frontend/Dockerfile`  
  - Compila el proyecto Svelte  
  - Sirve el build estático (nginx o node adapter)  

Ambos servicios usan variables de entorno (ver arriba).  
Coolify puede construirlos directamente desde este repositorio sin pasos manuales.  

---

## Base de datos
El sistema usa **PostgreSQL**.  
- En desarrollo: se levanta como servicio `db` dentro del `compose.yaml`.  
- En producción (Coolify): puede levantarse como servicio independiente y pasar las credenciales al backend mediante variables `POSTGRES_*`.  
