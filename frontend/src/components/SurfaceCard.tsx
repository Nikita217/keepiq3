import clsx from 'clsx';
import type { PropsWithChildren } from 'react';

export function SurfaceCard({
  children,
  tone = 'default',
  className,
}: PropsWithChildren<{ tone?: 'default' | 'accent' | 'warning'; className?: string }>) {
  return (
    <section
      className={clsx(
        'glass-surface rounded-[30px] p-4 shadow-soft sm:p-5',
        tone === 'accent' && 'glass-surface--accent',
        tone === 'warning' && 'glass-surface--warning',
        className,
      )}
    >
      {children}
    </section>
  );
}
