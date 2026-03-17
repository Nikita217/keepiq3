import { useState } from 'react';

export function EditorSheet({
  title,
  initialValue,
  onSave,
}: {
  title: string;
  initialValue: string;
  onSave: (value: string) => Promise<void>;
}) {
  const [value, setValue] = useState(initialValue);
  const [loading, setLoading] = useState(false);

  return (
    <div className="rounded-[24px] border border-line bg-white/75 p-4">
      <h4 className="text-sm font-bold text-ink">{title}</h4>
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="mt-3 min-h-24 w-full rounded-[18px] border border-line bg-white px-4 py-3 text-sm outline-none"
      />
      <button
        className="mt-3 rounded-full bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
        disabled={loading}
        onClick={async () => {
          setLoading(true);
          await onSave(value);
          setLoading(false);
        }}
      >
        Сохранить
      </button>
    </div>
  );
}
