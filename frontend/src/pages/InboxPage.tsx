import { useState } from 'react';

import { apiRequest } from '../api/client';
import type { InboxItem } from '../api/types';
import { AppShell } from '../components/AppShell';
import { EditorSheet } from '../components/EditorSheet';
import { EmptyState } from '../components/EmptyState';
import { SectionTitle } from '../components/SectionTitle';
import { SurfaceCard } from '../components/SurfaceCard';
import { useApi } from '../hooks/useApi';

export function InboxPage({ token }: { token: string }) {
  const { data, loading, reload } = useApi<InboxItem[]>('/inbox', token);
  const [editingId, setEditingId] = useState<number | null>(null);

  const convert = async (id: number, kind: 'task' | 'list') => {
    await apiRequest(`/inbox/${id}/convert-${kind}`, { method: 'POST', body: JSON.stringify({}) }, token);
    await reload();
  };

  const keep = async (id: number) => {
    await apiRequest(`/inbox/${id}/keep`, { method: 'POST' }, token);
    await reload();
  };

  return (
    <AppShell
      header={
        <>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">Страховка</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Входящие</h1>
          <p className="mt-2 text-sm text-muted">{loading ? 'Проверяю новые сообщения...' : 'Здесь всё, что ещё не хочется потерять или нужно разобрать вручную.'}</p>
        </>
      }
    >
      <SurfaceCard tone="warning">
        <SectionTitle title="Неразобранное" subtitle="Можно быстро превратить во что угодно или оставить как есть." />
        {!data?.length ? <EmptyState title="Во входящих пусто" body="Новые сообщения из бота появятся здесь автоматически." /> : null}
        <div className="space-y-3">
          {data?.map((item) => (
            <div key={item.id} className="glass-tile rounded-[26px] p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0 flex-1">
                  <h3 className="break-words text-[15px] font-bold leading-5 text-ink">
                    {item.ai_summary ?? item.raw_text?.slice(0, 60) ?? 'Новое входящее'}
                  </h3>
                  <p className="mt-2 break-words text-sm leading-5 text-muted">
                    {item.ai_detected_type ? `Похоже на ${item.ai_detected_type}` : 'Тип пока не определён'}
                  </p>
                </div>
                <span className="glass-chip shrink-0">{item.source_kind}</span>
              </div>
              <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-ink/86">{item.extracted_text ?? item.raw_text ?? 'Без текста'}</p>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                <button className="glass-button glass-button-primary w-full" onClick={() => convert(item.id, 'task')}>
                  Сохранить как задачу
                </button>
                <button className="glass-button glass-button-accent w-full" onClick={() => convert(item.id, 'list')}>
                  Сохранить как список
                </button>
                <button className="glass-button glass-button-secondary w-full" onClick={() => keep(item.id)}>
                  Оставить во входящих
                </button>
                <button className="glass-button glass-button-secondary w-full" onClick={() => setEditingId(editingId === item.id ? null : item.id)}>
                  {editingId === item.id ? 'Скрыть редактор' : 'Редактировать'}
                </button>
              </div>
              {editingId === item.id ? (
                <div className="mt-3">
                  <EditorSheet
                    title="Текст входящего"
                    initialValue={item.normalized_text ?? item.extracted_text ?? item.raw_text ?? ''}
                    onSave={async (value) => {
                      await apiRequest(`/inbox/${item.id}`, { method: 'PATCH', body: JSON.stringify({ normalized_text: value }) }, token);
                      setEditingId(null);
                      await reload();
                    }}
                  />
                </div>
              ) : null}
            </div>
          ))}
        </div>
      </SurfaceCard>
    </AppShell>
  );
}
