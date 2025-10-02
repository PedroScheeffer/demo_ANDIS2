@startuml
skinparam componentStyle rectangle
skinparam backgroundColor white
skinparam shadowing false

title Arquitectura de Infraestructura - Gestor de Proyectos

actor "Usuario" as user

cloud "Cloudflare DNS" as cloudflare

node "Laptop Ubuntu" {
    
    rectangle "Coolify\n(Gestión y Orquestación)" as coolify {
        
        component "Traefik\nReverse Proxy\n+ SSL" as traefik
        
        rectangle "Docker Compose" {
            component "Frontend\nSvelte\n:3000" as frontend
            component "Backend\nFastAPI\n:5000" as backend
            database "PostgreSQL\n:5432" as db
            
            ' Interfaces
            interface "HTTP/HTML" as ui_interface
            interface "REST API" as rest_interface
            interface "SQL" as sql_interface
            
            frontend -right- ui_interface
            backend -right- rest_interface
            backend -- sql_interface
            db -left- sql_interface
        }
        
        interface "HTTPS" as https_interface
        interface "HTTP" as http_interface
        
        traefik -right- https_interface
        traefik -- http_interface
    }
}

user --> cloudflare : HTTPS
cloudflare -right-> https_interface : DNS
http_interface -left-> ui_interface : demo.scheeffer.net
http_interface --> rest_interface : api.scheeffer.net
ui_interface --> rest_interface




@enduml