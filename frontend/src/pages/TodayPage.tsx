import { useMemo } from 'react';

import { apiRequest } from '../api/client';
import type { TodayResponse } from '../api/types';
import { AppShell } from '../components/AppShell';
import { EmptyState } from '../components/EmptyState';
import { SectionTitle } from '../components/SectionTitle';
import { SurfaceCard } from '../components/SurfaceCard';
import { TaskRow } from '../components/TaskRow';
import { useApi } from '../hooks/useApi';

export function TodayPage({ token }: { token: string }) {
  const { data, loading, reload } = useApi<TodayResponse>('/today', token);

  const total = useMemo(() => (data ? data.today.length + data.overdue.length : 0), [data]);

  const markDone = async (taskId: number) => {
    await apiRequest(`/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify({ is_done: true }) }, token);
    await reload();
  };

  const snooze = async (taskId: number) => {
    await apiRequest(`/tasks/${taskId}/snooze`, { method: 'POST', body: JSON.stringify({ kind: 'tomorrow_10' }) }, token);
    await reload();
  };

  return (
    <AppShell
      header={
        <>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">KeepiQ</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Сегодня</h1>
          <p className="mt-2 text-sm text-muted">{loading ? 'Обновляю список...' : `В фокусе ${total} задач, во входящих ${data?.inbox_count ?? 0}.`}</p>
        </>
      }
    >
      <SurfaceCard tone="accent" className="space-y-4">
        <SectionTitle title="Главное" subtitle="Просроченное и всё, что должно случиться сегодня." />
        {!data || total === 0 ? <EmptyState title="На сегодня тихо" body="Можно выдохнуть или разобрать входящие." /> : null}
        {data?.overdue.length ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <span className="glass-chip glass-chip--warning">Просрочено</span>
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">{data.overdue.length}</span>
            </div>
            <div className="space-y-3">
              {data.overdue.map((task) => (
                <TaskRow key={`overdue-${task.id}`} task={task} onDone={() => markDone(task.id)} onSnooze={() => snooze(task.id)} />
              ))}
            </div>
          </div>
        ) : null}
        {data?.today.length ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <span className="glass-chip glass-chip--accent">На сегодня</span>
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">{data.today.length}</span>
            </div>
            <div className="space-y-3">
              {data.today.map((task) => (
                <TaskRow key={`today-${task.id}`} task={task} onDone={() => markDone(task.id)} onSnooze={() => snooze(task.id)} />
              ))}
            </div>
          </div>
        ) : null}
      </SurfaceCard>
    </AppShell>
  );
}
