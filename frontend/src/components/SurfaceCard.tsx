import clsx from 'clsx';
import type { PropsWithChildren } from 'react';

export function SurfaceCard({ children, tone = 'default' }: PropsWithChildren<{ tone?: 'default' | 'accent' | 'warning' }>) {
  return (
    <section
      className={clsx(
        'rounded-[28px] border p-4 shadow-soft backdrop-blur-xl',
        tone === 'default' && 'border-line bg-card',
        tone === 'accent' && 'border-transparent bg-[var(--accent-soft)]',
        tone === 'warning' && 'border-transparent bg-[rgba(232,115,71,0.12)]',
      )}
    >
      {children}
    </section>
  );
}
