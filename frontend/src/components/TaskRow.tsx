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

function getMeta(task: Task) {
  if (task.description) return task.description;
  if (task.due_at) return `Срок: ${formatDue(task.due_at)}`;
  return 'Срок пока не указан';
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
    <div className="glass-tile rounded-[26px] p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="min-w-0 flex-1 break-words text-[15px] font-bold leading-5 text-ink">{task.title}</h3>
            <span className="glass-chip glass-chip--accent shrink-0">{formatDue(task.due_at)}</span>
          </div>
          <p className="mt-2 break-words text-sm leading-5 text-muted">{getMeta(task)}</p>
        </div>
      </div>
      {onDone || onSnooze ? (
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {onDone ? (
            <button className="glass-button glass-button-primary w-full" onClick={() => onDone(task)}>
              Выполнено
            </button>
          ) : null}
          {onSnooze ? (
            <button className="glass-button glass-button-secondary w-full" onClick={() => onSnooze(task)}>
              Отложить
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
