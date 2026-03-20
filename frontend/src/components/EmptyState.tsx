export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="glass-tile glass-empty rounded-[28px] p-6 text-center">
      <h3 className="text-base font-bold text-ink">{title}</h3>
      <p className="mt-2 text-sm leading-5 text-muted">{body}</p>
    </div>
  );
}
