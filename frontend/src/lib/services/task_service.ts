import type { Task, TaskCreate } from '$lib/models';

const API_BASE_URL = 'http://localhost:5000/api';

export async function getTasks(projectId: number): Promise<Task[]> {
  const response = await fetch(`${API_BASE_URL}/tasks/project/${projectId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`);
  }
  return response.json();
}

export async function createTask(task: TaskCreate): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/tasks/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  });
  if (!response.ok) {
    throw new Error(`Failed to create task: ${response.statusText}`);
  }
  return response.json();
}

export async function updateTask(id: number, task: Partial<Task>): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  });
  if (!response.ok) {
    throw new Error(`Failed to update task: ${response.statusText}`);
  }
  return response.json();
}

export async function toggleTaskComplete(taskId: number): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/complete`, {
    method: 'PATCH',
  });
  if (!response.ok) {
    throw new Error(`Failed to toggle task completion: ${response.statusText}`);
  }
  return response.json();
}
