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
            <div key={item.id} className="glass-tile rounded-[26px] p-3">
              <button
                className="flex w-full items-start justify-between gap-3 rounded-[20px] px-1 py-1 text-left"
                onClick={() => {
                  if (active?.id === item.id) {
                    setActive(null);
                    return;
                  }
                  void openList(item.id);
                }}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="break-words text-[15px] font-bold leading-5 text-ink">{item.title}</h3>
                    {active?.id === item.id ? <span className="glass-chip glass-chip--accent">Открыт</span> : null}
                  </div>
                  <p className="mt-2 break-words text-sm leading-5 text-muted">{item.description ?? 'Без описания'}</p>
                </div>
                <span className="glass-chip shrink-0">{active?.id === item.id ? 'Свернуть' : 'Открыть'}</span>
              </button>

              {active?.id === item.id ? (
                <div className="mt-4 space-y-3 border-t border-[rgba(22,33,43,0.08)] pt-4">
                  <EditorSheet
                    title="Название списка"
                    initialValue={active.title}
                    onSave={async (value) => {
                      await apiRequest(`/lists/${active.id}`, { method: 'PATCH', body: JSON.stringify({ title: value }) }, token);
                      await reload();
                      await openList(active.id);
                    }}
                  />
                  {!active.tasks.length ? <EmptyState title="Внутри пока пусто" body="Список есть, но в нём ещё нет отдельных пунктов." /> : null}
                  <div className="space-y-3">
                    {active.tasks.map((task) => <TaskRow key={task.id} task={task} />)}
                  </div>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      </SurfaceCard>
    </AppShell>
  );
}
