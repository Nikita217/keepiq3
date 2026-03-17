import { useState } from 'react';

import type { TaskList, TaskListDetail } from '../api/types';
import { apiRequest } from '../api/client';
import { AppShell } from '../components/AppShell';
import { EditorSheet } from '../components/EditorSheet';
import { EmptyState } from '../components/EmptyState';
import { SectionTitle } from '../components/SectionTitle';
import { SurfaceCard } from '../components/SurfaceCard';
import { TaskRow } from '../components/TaskRow';
import { useApi } from '../hooks/useApi';

export function ListsPage({ token }: { token: string }) {
  const { data, loading, reload } = useApi<TaskList[]>('/lists', token);
  const [active, setActive] = useState<TaskListDetail | null>(null);

  const openList = async (id: number) => {
    const detail = await apiRequest<TaskListDetail>(`/lists/${id}`, {}, token);
    setActive(detail);
  };

  return (
    <AppShell
      header={
        <>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">Коллекции</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Списки</h1>
          <p className="mt-2 text-sm text-muted">Покупки, подготовки, наборы дел и любые многошаговые штуки.</p>
        </>
      }
    >
      <SurfaceCard>
        <SectionTitle title="Все списки" subtitle={loading ? 'Загружаю...' : 'Открой список, чтобы отметить пункты выполненными или поправить текст.'} />
        {!data?.length ? <EmptyState title="Списков пока нет" body="Как только бот распознает несколько пунктов, они появятся здесь." /> : null}
        <div className="space-y-3">
          {data?.map((item) => (
            <button key={item.id} className="block w-full rounded-[24px] border border-line bg-white/70 p-4 text-left" onClick={() => openList(item.id)}>
              <h3 className="text-[15px] font-bold text-ink">{item.title}</h3>
              <p className="mt-1 text-sm text-muted">{item.description ?? 'Без описания'}</p>
            </button>
          ))}
        </div>
      </SurfaceCard>

      {active ? (
        <SurfaceCard tone="accent">
          <SectionTitle title={active.title} subtitle="Пункты внутри списка — это обычные задачи, поэтому они попадают в Сегодня и поиск." />
          <EditorSheet
            title="Название списка"
            initialValue={active.title}
            onSave={async (value) => {
              await apiRequest(`/lists/${active.id}`, { method: 'PATCH', body: JSON.stringify({ title: value }) }, token);
              await reload();
              await openList(active.id);
            }}
          />
          <div className="mt-4 space-y-3">
            {active.tasks.map((task) => <TaskRow key={task.id} task={task} />)}
          </div>
        </SurfaceCard>
      ) : null}
    </AppShell>
  );
}
