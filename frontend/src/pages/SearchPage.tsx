import { useState } from 'react';

import type { SearchResponse } from '../api/types';
import { AppShell } from '../components/AppShell';
import { EmptyState } from '../components/EmptyState';
import { SectionTitle } from '../components/SectionTitle';
import { SurfaceCard } from '../components/SurfaceCard';
import { useApi } from '../hooks/useApi';

export function SearchPage({ token }: { token: string }) {
  const [query, setQuery] = useState('');
  const { data, loading } = useApi<SearchResponse>(`/search?q=${encodeURIComponent(query || 'кот')}`, token, query.length < 2);

  return (
    <AppShell
      header={
        <>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">Найти быстро</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Поиск</h1>
          <p className="mt-2 text-sm text-muted">Ищи по задачам, спискам и даже по тому, что осталось во входящих.</p>
        </>
      }
    >
      <SurfaceCard>
        <SectionTitle title="Смысловой поиск" subtitle="Можно искать по памяти, а не только по точным словам." />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Например: билет на концерт или что купить коту"
          className="glass-input"
        />
        <div className="mt-4 space-y-3">
          {query.length < 2 ? <EmptyState title="Начни вводить запрос" body="Достаточно пары слов, дальше сервис сам поднимет подходящие задачи, списки и входящие." /> : null}
          {!loading && query.length >= 2 && !data?.results.length ? <EmptyState title="Ничего не нашлось" body="Попробуй пересказать запрос чуть иначе: по человеку, месту, теме или действию." /> : null}
          {data?.results.map((item) => (
            <div key={`${item.kind}-${item.id}`} className="glass-tile rounded-[26px] p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <h3 className="break-words text-[15px] font-bold leading-5 text-ink">{item.title}</h3>
                <span className="glass-chip glass-chip--accent shrink-0">{item.kind}</span>
              </div>
              <p className="mt-2 break-words text-sm leading-5 text-muted">{item.subtitle ?? 'Без подзаголовка'}</p>
              {item.matched_text ? <p className="mt-2 break-words text-sm leading-6 text-ink/86">{item.matched_text}</p> : null}
            </div>
          ))}
        </div>
      </SurfaceCard>
    </AppShell>
  );
}
