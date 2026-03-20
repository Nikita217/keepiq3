const DEFAULT_LOCAL_API_BASE = 'http://localhost:8000/api/v1';

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  (window.location.hostname === 'localhost' ? DEFAULT_LOCAL_API_BASE : '');

export async function apiRequest<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  if (!API_BASE) {
    throw new Error('VITE_API_BASE_URL is not configured in this frontend build.');
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const payload = await response.text();
    throw new Error(payload || 'Request failed');
  }

  return response.json() as Promise<T>;
}
