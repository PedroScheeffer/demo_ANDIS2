import type { Project, ProjectCreate } from '$lib/models';
import { getAuthToken } from './auth_service';

// Resolve API base URL from Vite env at build time, fallback to localhost for local dev.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000/api';

function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
}

export async function getProjects(): Promise<Project[]> {
  let retry = 1;
  while (retry <= 6) {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      headers: getAuthHeaders(),
    });
    if (response.ok) {
      return response.json();
    }
    // wait and then retry
    await new Promise((resolve) => setTimeout(resolve, retry * 1000));
    retry += 1;
  }
  throw new Error('Failed to fetch projects after multiple retries');
}

export async function getProject(id: number): Promise<Project> {
  const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch project: ${response.statusText}`);
  }
  return response.json();
}

export async function createProject(project: ProjectCreate, userId: number): Promise<Project> {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ ...project, user_id: userId }),
  });
  if (!response.ok) {
    throw new Error(`Failed to create project: ${response.statusText}`);
  }
  return response.json();
}
