import type { Project, ProjectCreate } from '$lib/models';
import { getAuthToken } from './auth_service';

// Resolve API base URL from Vite env at build time, fallback to localhost for local dev.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.facumar93.win/api';

// Fallback: intenta leer el token que guarda el flujo de Google (/auth/callback)
function getGoogleTokenFallback(): string | null {
  try {
    if (typeof window === 'undefined') return null;
    const raw = localStorage.getItem('auth_response');
    return raw ? (JSON.parse(raw)?.access_token ?? null) : null;
  } catch {
    return null;
  }
}

// --- 🔒 Cambios acá ---
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken() || getGoogleTokenFallback();
  if (!token) throw new Error('NO_TOKEN'); // evita fetch sin auth
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };
}

async function handle(r: Response) {
  if (r.status === 401) {
    localStorage.removeItem('auth_response');
    location.replace('/login');
    throw new Error('Unauthorized');
  }
  if (!r.ok) throw new Error(r.statusText);
  return r.json();
}
// --- 🔒 Fin cambios ---

export async function getProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    headers: getAuthHeaders(),
  });
  return handle(response);
}

export async function getProject(id: number): Promise<Project> {
  const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
    headers: getAuthHeaders(),
  });
  return handle(response);
}

export async function createProject(project: ProjectCreate, userId: number): Promise<Project> {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ ...project, user_id: userId }),
  });
  return handle(response);
}
