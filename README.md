# Mini Demo - Gestor de Proyectos

## Descripción
API REST para gestión básica de proyectos y tareas con autenticación JWT. Demo para TFU3 - Soluciones de Arquitectura.

## Arquitectura
- **Escalabilidad**: Vertical (Docker container escalable)
- **Base de datos**: PostgreSQL (ACID)
- **Contenedores**: Docker + docker-compose
- **API**: REST stateless con JWT


## Instalación y Ejecución

### Con Docker (recomendado)
#### DEV
```
docker compose -f compose.dev.yaml up -d --force-recreate --build
```
#### PROD
```
docker compose up -d (--build --force-recreate opcional)
```
El backend tiene hotreload, no es necesario volver a reiniciar el container para ver cambios. 



