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
      <SurfaceCard>
        <SectionTitle title="Неразобранное" subtitle="Можно быстро превратить во что угодно или оставить как есть." />
        {!data?.length ? <EmptyState title="Во входящих пусто" body="Новые сообщения из бота появятся здесь автоматически." /> : null}
        <div className="space-y-3">
          {data?.map((item) => (
            <div key={item.id} className="rounded-[24px] border border-line bg-white/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h3 className="text-[15px] font-bold text-ink">{item.ai_summary ?? item.raw_text?.slice(0, 60) ?? 'Новое входящее'}</h3>
                  <p className="mt-1 text-sm text-muted">{item.ai_detected_type ? `Похоже на ${item.ai_detected_type}` : 'Тип пока не определён'}</p>
                </div>
                <span className="rounded-full bg-[var(--accent-soft)] px-3 py-1 text-xs font-semibold text-[var(--accent)]">{item.source_kind}</span>
              </div>
              <p className="mt-3 whitespace-pre-wrap text-sm text-ink/85">{item.extracted_text ?? item.raw_text ?? 'Без текста'}</p>
              <div className="mt-4 grid grid-cols-2 gap-2">
                <button className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white" onClick={() => convert(item.id, 'task')}>Сохранить как задачу</button>
                <button className="rounded-full bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white" onClick={() => convert(item.id, 'list')}>Сохранить как список</button>
                <button className="rounded-full border border-line px-4 py-2 text-sm font-semibold text-ink" onClick={() => keep(item.id)}>Оставить во входящих</button>
                <button className="rounded-full border border-line px-4 py-2 text-sm font-semibold text-ink" onClick={() => setEditingId(editingId === item.id ? null : item.id)}>Редактировать</button>
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
