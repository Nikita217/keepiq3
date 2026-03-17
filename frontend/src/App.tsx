import { HashRouter, Route, Routes } from 'react-router-dom';

import { AppShell } from './components/AppShell';
import { EmptyState } from './components/EmptyState';
import { useAuth } from './hooks/useAuth';
import { setupTelegramTheme } from './lib/telegram';
import { CalendarPage } from './pages/CalendarPage';
import { InboxPage } from './pages/InboxPage';
import { ListsPage } from './pages/ListsPage';
import { SearchPage } from './pages/SearchPage';
import { TodayPage } from './pages/TodayPage';

setupTelegramTheme();

function ShellState({ title, body }: { title: string; body: string }) {
  return (
    <AppShell header={<><p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">KeepiQ</p><h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">{title}</h1></>}>
      <EmptyState title={title} body={body} />
    </AppShell>
  );
}

export default function App() {
  const { token, loading, error } = useAuth();

  return (
    <HashRouter>
      {loading ? <ShellState title="Подключаюсь" body="Проверяю Telegram-подпись и поднимаю твои данные." /> : null}
      {!loading && (error || !token) ? <ShellState title="Не удалось войти" body={error ?? 'Проверь API и Telegram initData.'} /> : null}
      {!loading && token ? (
        <Routes>
          <Route path="/" element={<TodayPage token={token} />} />
          <Route path="/inbox" element={<InboxPage token={token} />} />
          <Route path="/calendar" element={<CalendarPage token={token} />} />
          <Route path="/lists" element={<ListsPage token={token} />} />
          <Route path="/search" element={<SearchPage token={token} />} />
        </Routes>
      ) : null}
    </HashRouter>
  );
}
