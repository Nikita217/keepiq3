export function SectionTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-4 flex items-end justify-between gap-3">
      <div className="min-w-0">
        <h2 className="break-words text-[1.15rem] font-extrabold tracking-tight text-ink">{title}</h2>
        {subtitle ? <p className="mt-1 break-words text-sm leading-5 text-muted">{subtitle}</p> : null}
      </div>
    </div>
  );
}
