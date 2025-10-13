// Resolve API base URL from Vite env at build time, fallback to localhost for local dev.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000/api';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    username: string;
  };
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();

  // Store token and auth response in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('auth_response', JSON.stringify(data));
  }

  return data;
}

export async function register(username: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(error.detail || 'Registration failed');
  }

  const data = await response.json();

  // Store token and auth response in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('auth_response', JSON.stringify(data));
  }

  return data;
}

export async function logout(): Promise<void> {
  // Clear local session data
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_response');
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}
