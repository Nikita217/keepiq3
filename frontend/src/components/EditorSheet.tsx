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
    <div className="glass-tile rounded-[26px] p-4">
      <h4 className="text-sm font-bold text-ink">{title}</h4>
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="glass-input mt-3 min-h-[7.5rem]"
      />
      <button
        className="glass-button glass-button-accent mt-3 w-full disabled:opacity-60 sm:w-auto"
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
