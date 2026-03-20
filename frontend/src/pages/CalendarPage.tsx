import { useMemo, useState } from 'react';

import type { Task } from '../api/types';
import { AppShell } from '../components/AppShell';
import { EmptyState } from '../components/EmptyState';
import { SectionTitle } from '../components/SectionTitle';
import { SurfaceCard } from '../components/SurfaceCard';
import { TaskRow } from '../components/TaskRow';
import { useApi } from '../hooks/useApi';

const weekdayFormatter = new Intl.DateTimeFormat('ru-RU', { weekday: 'short' });
const monthFormatter = new Intl.DateTimeFormat('ru-RU', { month: 'long', year: 'numeric' });
const selectedDayFormatter = new Intl.DateTimeFormat('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' });

function toDateValue(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function fromDateValue(value: string) {
  const [year, month, day] = value.split('-').map(Number);
  return new Date(year, month - 1, day);
}

function shiftMonth(value: string, delta: number) {
  const current = fromDateValue(value);
  const next = new Date(current.getFullYear(), current.getMonth() + delta, 1);
  const lastDay = new Date(next.getFullYear(), next.getMonth() + 1, 0).getDate();
  next.setDate(Math.min(current.getDate(), lastDay));
  return toDateValue(next);
}

function shiftDay(value: string, delta: number) {
  const current = fromDateValue(value);
  current.setDate(current.getDate() + delta);
  return toDateValue(current);
}

function buildCalendar(value: string) {
  const selected = fromDateValue(value);
  const monthStart = new Date(selected.getFullYear(), selected.getMonth(), 1);
  const monthEnd = new Date(selected.getFullYear(), selected.getMonth() + 1, 0);
  const startOffset = (monthStart.getDay() + 6) % 7;
  const cells: Array<{ value: string; label: number; inMonth: boolean }> = [];

  for (let index = 0; index < 42; index += 1) {
    const cellDate = new Date(monthStart);
    cellDate.setDate(index - startOffset + 1);
    cells.push({
      value: toDateValue(cellDate),
      label: cellDate.getDate(),
      inMonth: cellDate >= monthStart && cellDate <= monthEnd,
    });
  }

  return cells;
}

export function CalendarPage({ token }: { token: string }) {
  const [date, setDate] = useState(() => toDateValue(new Date()));
  const { data, loading } = useApi<Task[]>(`/calendar?date_value=${date}`, token);
  const selectedDate = fromDateValue(date);
  const todayValue = toDateValue(new Date());
  const calendarDays = useMemo(() => buildCalendar(date), [date]);
  const weekdayLabels = useMemo(
    () =>
      Array.from({ length: 7 }, (_, index) => {
        const day = new Date(2024, 0, index + 1);
        return weekdayFormatter.format(day).slice(0, 2);
      }),
    [],
  );

  return (
    <AppShell
      header={
        <>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">План</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Календарь</h1>
          <p className="mt-2 text-sm text-muted">Открой нужную дату и посмотри все задачи и напоминания на неё.</p>
        </>
      }
    >
      <SurfaceCard className="space-y-4">
        <SectionTitle title="Выбранный день" subtitle="Теперь можно листать месяц, а не искать дату через системный инпут." />
        <div className="glass-tile rounded-[28px] p-4">
          <div className="flex items-center justify-between gap-3">
            <button className="glass-button glass-button-secondary h-11 w-11 shrink-0 px-0" onClick={() => setDate(shiftMonth(date, -1))}>
              ←
            </button>
            <div className="min-w-0 text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted">Месяц</p>
              <h3 className="mt-1 break-words text-lg font-bold capitalize tracking-tight text-ink">{monthFormatter.format(selectedDate)}</h3>
            </div>
            <button className="glass-button glass-button-secondary h-11 w-11 shrink-0 px-0" onClick={() => setDate(shiftMonth(date, 1))}>
              →
            </button>
          </div>

          <div className="mt-4 grid grid-cols-7 gap-2">
            {weekdayLabels.map((day) => (
              <span key={day} className="text-center text-[11px] font-semibold uppercase tracking-[0.14em] text-muted">
                {day}
              </span>
            ))}
            {calendarDays.map((day) => {
              const isSelected = day.value === date;
              const isToday = day.value === todayValue;

              return (
                <button
                  key={day.value}
                  className={[
                    'min-h-[2.85rem] rounded-[18px] px-0 text-sm font-semibold transition',
                    day.inMonth ? 'text-ink' : 'text-muted/45',
                    isSelected ? 'glass-state-active text-ink shadow-[0_14px_28px_rgba(13,20,28,0.14)]' : 'glass-tile',
                    !isSelected && isToday ? 'border border-[rgba(49,95,87,0.24)] text-[var(--accent-deep)]' : '',
                  ].join(' ')}
                  onClick={() => setDate(day.value)}
                >
                  {day.label}
                </button>
              );
            })}
          </div>

          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            <button className="glass-button glass-button-secondary w-full" onClick={() => setDate(todayValue)}>
              Сегодня
            </button>
            <button className="glass-button glass-button-secondary w-full" onClick={() => setDate(shiftDay(todayValue, 1))}>
              Завтра
            </button>
            <button className="glass-button glass-button-secondary w-full" onClick={() => setDate(shiftDay(todayValue, 7))}>
              Через неделю
            </button>
          </div>
        </div>

        <div className="glass-tile rounded-[28px] p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted">Выбрано</p>
              <h3 className="mt-1 break-words text-lg font-bold capitalize tracking-tight text-ink">{selectedDayFormatter.format(selectedDate)}</h3>
              <p className="mt-2 text-sm leading-5 text-muted">
                {loading
                  ? 'Обновляю задачи на этот день...'
                  : data?.length
                    ? `Найдено ${data.length} ${data.length === 1 ? 'элемент' : 'элементов'} в расписании.`
                    : 'На этот день пока ничего не запланировано.'}
              </p>
            </div>
            <input type="date" value={date} onChange={(event) => setDate(event.target.value)} className="glass-input sm:max-w-[13rem]" />
          </div>
        </div>

        <div className="space-y-3">
          {!loading && !data?.length ? <EmptyState title="На эту дату пусто" body="Если срок наступит позже, задача всё равно останется в списках и поиске." /> : null}
          {data?.map((task) => <TaskRow key={task.id} task={task} />)}
        </div>
      </SurfaceCard>
    </AppShell>
  );
}
