import { useEffect, useState } from 'react';

import { API_BASE, apiRequest } from '../api/client';
import type { AuthResponse } from '../api/types';
import { getInitData } from '../lib/telegram';

const TOKEN_KEY = 'keepiq_token';

function isLocalHost(hostname: string) {
  return hostname === 'localhost' || hostname === '127.0.0.1';
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(() => {
    const initData = getInitData();
    if (!initData && !isLocalHost(window.location.hostname)) {
      localStorage.removeItem(TOKEN_KEY);
      return null;
    }
    return localStorage.getItem(TOKEN_KEY);
  });
  const [user, setUser] = useState<AuthResponse['user'] | null>(null);
  const [loading, setLoading] = useState(!token);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      setLoading(false);
      return;
    }

    const run = async () => {
      try {
        const initData = getInitData();
        if (!initData && !isLocalHost(window.location.hostname)) {
          throw new Error('Mini App открыт вне Telegram WebApp. Открой его кнопкой в боте.');
        }
        const response = initData
          ? await apiRequest<AuthResponse>('/auth/telegram', { method: 'POST', body: JSON.stringify({ init_data: initData }) })
          : await apiRequest<AuthResponse>('/auth/dev', { method: 'POST' });
        localStorage.setItem(TOKEN_KEY, response.access_token);
        setToken(response.access_token);
        setUser(response.user);
      } catch (err) {
        const baseMessage = err instanceof Error ? err.message : 'Не удалось авторизоваться.';
        const initDataPresent = getInitData() ? 'yes' : 'no';
        setError(`${baseMessage} | api=${API_BASE || 'missing'} | initData=${initDataPresent}`);
      } finally {
        setLoading(false);
      }
    };

    void run();
  }, [token]);

  return { token, user, loading, error };
}
