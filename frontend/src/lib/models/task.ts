export interface Task {
  id?: number;
  detalle: string;
  project_id: number;
  user_id?: number;
  parent_task_id?: number;
  created_at?: Date;
  completed: boolean;
}

export interface TaskCreate {
  detalle: string;
  project_id: number;
  user_id?: number;
  parent_task_id?: number;
}

export function canHaveSubtasks(task: Task): boolean {
  return !task.completed;
}

export function isSubtask(task: Task): boolean {
  return task.parent_task_id !== undefined && task.parent_task_id !== null;
}
