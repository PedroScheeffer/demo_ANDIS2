@startuml

skinparam componentStyle rectangle
skinparam backgroundColor white
skinparam shadowing false

title Diagrama de Microservicios - Gestor de Proyectos

package "Frontend (Svelte)" {
    component "View" as view
    component "Services" as fe_services

    view --> fe_services
}

package "Microservices (FastAPI)" {
    package "User Service (puerto 5000)" {
        component "Auth Router" as auth_router
        component "User Service" as s_user
        component "User Repository" as r_user

        auth_router --> s_user
        s_user --> r_user
    }

    package "Project Service (puerto 5000)" {
        component "Project Router" as proj_router
        component "Project Service" as s_project
        component "Project Repository" as r_project

        proj_router --> s_project
        s_project --> r_project
    }

    package "Task Service (puerto 5000)" {
        component "Task Router" as task_router
        component "Task Service" as s_task
        component "Task Repository" as r_task

        task_router --> s_task
        s_task --> r_task
    }

}

database "PostgreSQL" as db

' Interfaces
interface "REST API" as rest

' Inter-service communication
proj_router ..> auth_router : verify_token
task_router ..> auth_router : verify_token
s_task ..> s_project : check_project_exists

' External connections
fe_services -right-> rest
rest -right-> auth_router
rest -right-> proj_router
rest -right-> task_router

r_user -down-> db
r_project -down-> db
r_task -down-> db

@enduml

