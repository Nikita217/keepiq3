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
    <nav
      className="glass-surface fixed left-1/2 z-20 grid w-[min(calc(100%-24px),30rem)] -translate-x-1/2 grid-cols-5 gap-1 rounded-[30px] p-2 shadow-soft"
      style={{ bottom: 'calc(env(safe-area-inset-bottom, 0px) + 12px)' }}
    >
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          className={({ isActive }) =>
            clsx(
              'min-w-0 rounded-[22px] px-2 py-3 text-center text-[11px] font-semibold leading-[1.15] tracking-[-0.01em] transition',
              isActive
                ? 'bg-[rgba(16,27,37,0.9)] text-[rgba(247,250,252,0.98)] shadow-[0_12px_25px_rgba(16,27,37,0.2)]'
                : 'text-ink/72 hover:bg-white/35',
            )
          }
        >
          <span className="block break-words">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
