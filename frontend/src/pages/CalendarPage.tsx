import { useState } from 'react';

import type { Task } from '../api/types';
import { AppShell } from '../components/AppShell';
import { EmptyState } from '../components/EmptyState';
import { SectionTitle } from '../components/SectionTitle';
import { SurfaceCard } from '../components/SurfaceCard';
import { TaskRow } from '../components/TaskRow';
import { useApi } from '../hooks/useApi';

export function CalendarPage({ token }: { token: string }) {
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const { data, loading } = useApi<Task[]>(`/calendar?date_value=${date}`, token);

  return (
    <AppShell
      header={
        <>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">План</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Календарь</h1>
          <p className="mt-2 text-sm text-muted">Открой нужную дату и посмотри все задачи и напоминания на неё.</p>
        </>
      }
    >
      <SurfaceCard>
        <SectionTitle title="Выбранный день" subtitle="Календарь работает поверх задач и напоминаний, без отдельной сущности событий." />
        <input type="date" value={date} onChange={(event) => setDate(event.target.value)} className="w-full rounded-[20px] border border-line bg-white px-4 py-3 text-sm" />
        <div className="mt-4 space-y-3">
          {!loading && !data?.length ? <EmptyState title="На эту дату пусто" body="Если срок наступит позже, задача всё равно останется в списках и поиске." /> : null}
          {data?.map((task) => <TaskRow key={task.id} task={task} />)}
        </div>
      </SurfaceCard>
    </AppShell>
  );
}
