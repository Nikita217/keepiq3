import clsx from 'clsx';
import { NavLink } from 'react-router-dom';

const tabs = [
  { to: '/', label: '\u0421\u0435\u0433\u043e\u0434\u043d\u044f' },
  { to: '/inbox', label: '\u0412\u0445\u043e\u0434\u044f\u0449\u0438\u0435' },
  { to: '/calendar', label: '\u041a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044c' },
  { to: '/lists', label: '\u0421\u043f\u0438\u0441\u043a\u0438' },
  { to: '/search', label: '\u041f\u043e\u0438\u0441\u043a' },
];

export function BottomNav() {
  return (
    <nav
      className="glass-surface fixed left-1/2 z-20 grid w-[min(calc(100%-24px),30rem)] -translate-x-1/2 grid-cols-5 gap-1 rounded-[30px] p-2 shadow-soft"
      style={{ bottom: 'calc(var(--app-bottom-inset) + 12px)' }}
    >
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          className={({ isActive }) =>
            clsx(
              'min-w-0 rounded-[22px] px-2 py-3 text-center text-[11px] font-semibold leading-[1.15] tracking-[-0.01em] transition',
              isActive ? 'glass-state-active text-ink' : 'text-ink/72 hover:bg-white/45',
            )
          }
        >
          <span className="block break-words">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}