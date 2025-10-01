export interface Project {
  id?: number;
  nombre: string;
  description?: string;
  user_id: number;
  created_at?: Date;
}

export interface ProjectCreate {
  nombre: string;
  description?: string;
}

export function canBeDeleted(project: Project): boolean {
  return true;
}
