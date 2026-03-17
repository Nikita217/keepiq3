import type { Task } from '../api/types';

function formatDue(value: string | null) {
  if (!value) return 'Без даты';
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

export function TaskRow({
  task,
  onDone,
  onSnooze,
}: {
  task: Task;
  onDone?: (task: Task) => void;
  onSnooze?: (task: Task) => void;
}) {
  return (
    <div className="rounded-[22px] border border-line bg-white/70 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-[15px] font-bold text-ink">{task.title}</h3>
          <p className="mt-1 text-sm text-muted">{task.description ?? formatDue(task.due_at)}</p>
        </div>
        <span className="rounded-full bg-[var(--accent-soft)] px-3 py-1 text-xs font-semibold text-[var(--accent)]">{formatDue(task.due_at)}</span>
      </div>
      <div className="mt-3 flex gap-2">
        {onDone ? <button className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white" onClick={() => onDone(task)}>Выполнено</button> : null}
        {onSnooze ? <button className="rounded-full border border-line px-4 py-2 text-sm font-semibold text-ink" onClick={() => onSnooze(task)}>Отложить</button> : null}
      </div>
    </div>
  );
}
