Diagrama de clases.

::: mermaid
classDiagram
class Proyecto {
    -string nombre
}

class Tarea {
    -string detalle   
}

class Usuario {
    -string nombre
}

Proyecto "1" *-- "n" Tarea : Varias 
Tarea -- Tarea : SubTareas
Usuario *-- Proyecto
Usuario -- Tarea 
:::