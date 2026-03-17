import type { PropsWithChildren, ReactNode } from 'react';

import { BottomNav } from './BottomNav';

export function AppShell({ children, header }: PropsWithChildren<{ header: ReactNode }>) {
  return (
    <div className="mx-auto min-h-screen max-w-md px-3 pb-28 pt-4">
      <div className="rounded-[32px] border border-line bg-card p-4 shadow-soft backdrop-blur-xl">
        {header}
      </div>
      <div className="mt-4 space-y-4">{children}</div>
      <BottomNav />
    </div>
  );
}
