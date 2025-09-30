export interface User {
  id?: number;
  nombre: string;
  email: string;
  password_hash: string;
  created_at?: Date;
}

export interface UserCreate {
  nombre: string;
  email: string;
  password: string;
}

export function canCreateProject(user: User): boolean {
  return true;
}
