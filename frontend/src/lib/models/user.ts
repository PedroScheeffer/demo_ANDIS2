export interface User {
  id?: number;
  nombre: string;
  password_hash?: string;
  created_at?: Date;
}

export interface UserCreate {
  nombre: string;
  password: string;
}

export function canCreateProject(user: User): boolean {
  return true;
}
