Diagrama de clases.

::: mermaid
classDiagram
class Proyecto {
    -int id
    -string nombre
    -string description
    -int user_id
    -datetime created_at
    +can_be_deleted() bool
}

class Tarea {
    -int id
    -string detalle
    -int project_id
    -int user_id
    -int parent_task_id
    -bool completed
    -datetime created_at
    +can_have_subtasks() bool
    +is_subtask() bool
}

class Usuario {
    -int id
    -string nombre
    -string password_hash
    -datetime created_at
    +can_create_project() bool
}

Proyecto "1" *-- "n" Tarea : contiene
Tarea "1" o-- "n" Tarea : SubTareas
Usuario "1" *-- "n" Proyecto : posee
Usuario "1" -- "n" Tarea : asignada a
:::