import clsx from 'clsx';
import { NavLink } from 'react-router-dom';

const tabs = [
  { to: '/', label: 'Сегодня' },
  { to: '/inbox', label: 'Входящие' },
  { to: '/calendar', label: 'Календарь' },
  { to: '/lists', label: 'Списки' },
  { to: '/search', label: 'Поиск' },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-4 left-1/2 z-20 flex w-[calc(100%-24px)] max-w-md -translate-x-1/2 gap-1 rounded-[28px] border border-line bg-[rgba(255,251,247,0.88)] p-2 shadow-soft backdrop-blur-xl">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          className={({ isActive }) =>
            clsx(
              'flex-1 rounded-[22px] px-3 py-3 text-center text-[12px] font-semibold transition',
              isActive ? 'bg-[var(--accent)] text-white' : 'text-muted',
            )
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
