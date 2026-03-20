import type { PropsWithChildren, ReactNode } from 'react';

import { BottomNav } from './BottomNav';

export function AppShell({ children, header }: PropsWithChildren<{ header: ReactNode }>) {
  return (
    <div
      className="mx-auto min-h-screen w-full max-w-[30rem] px-4 sm:px-5"
      style={{
        paddingTop: 'calc(var(--app-top-inset) + 20px)',
        paddingBottom: 'calc(var(--app-bottom-inset) + 8.75rem)',
      }}
    >
      <div className="glass-surface glass-surface--strong rounded-[34px] p-5 shadow-soft sm:p-6">
        <div className="min-w-0 break-words">{header}</div>
      </div>
      <div className="mt-4 space-y-4">{children}</div>
      <BottomNav />
    </div>
  );
}