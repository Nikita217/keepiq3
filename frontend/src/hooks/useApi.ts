import { useCallback, useEffect, useState } from 'react';

import { apiRequest } from '../api/client';

export function useApi<T>(path: string, token?: string, skip = false) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!skip);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!token || skip) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<T>(path, {}, token);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [path, skip, token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, loading, error, reload, setData };
}
