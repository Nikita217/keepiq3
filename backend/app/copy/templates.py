from __future__ import annotations

from datetime import datetime

from app.ai.schemas import DetectedType, StructuredUnderstanding
from app.core.clock import user_tz
from app.core.config import get_settings
from app.models.task import Task

MONTHS = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def format_human_datetime(dt: datetime | None, timezone_name: str | None = None) -> str | None:
    if not dt:
        return None
    tz = user_tz(timezone_name or get_settings().default_timezone)
    local_dt = dt.astimezone(tz) if dt.tzinfo else dt.replace(tzinfo=tz)
    return f"{local_dt.day} {MONTHS[local_dt.month]} в {local_dt:%H:%M}"


def _list_preview(understanding: StructuredUnderstanding) -> str | None:
    if understanding.detected_type != DetectedType.list or not understanding.list_items:
        return None
    lines = [f"- {item.title}" for item in understanding.list_items[:4]]
    if len(understanding.list_items) > 4:
        lines.append(f"- ...и ещё {len(understanding.list_items) - 4}")
    return "Список сейчас вижу так:\n" + "\n".join(lines)


def _tips_block(understanding: StructuredUnderstanding) -> str | None:
    if not understanding.helpful_tips:
        return None
    lines = [f"- {tip}" for tip in understanding.helpful_tips]
    return "Может пригодиться:\n" + "\n".join(lines)


def build_analysis_message(understanding: StructuredUnderstanding, timezone_name: str | None = None) -> str:
    parts = [understanding.assistant_reply.strip()]

    due_at = format_human_datetime(understanding.due_at, timezone_name)
    if due_at and understanding.detected_type != DetectedType.list:
        parts.append(f"Срок сейчас понимаю как {due_at}.")

    list_preview = _list_preview(understanding)
    if list_preview:
        parts.append(list_preview)

    tips_block = _tips_block(understanding)
    if tips_block:
        parts.append(tips_block)

    return "\n\n".join(part for part in parts if part)


def build_keep_inbox_message() -> str:
    return "Оставил это во входящих, чтобы не потерялось."


def build_task_saved_message(task: Task, timezone_name: str | None = None) -> str:
    if task.due_at:
        return f"Сохранил задачу. Напомню {format_human_datetime(task.due_at, timezone_name)}."
    return "Сохранил как задачу без даты."


def build_list_saved_message(title: str, count: int) -> str:
    return f"Сохранил список «{title}». Внутри {count} пунктов."


def build_tasks_split_message(count: int) -> str:
    return f"Разбил это на {count} отдельных задач."


def build_reminder_message(task: Task) -> str:
    if task.due_at:
        return f"Напоминаю: {task.title}. Время уже рядом."
    return f"Напоминаю про задачу: {task.title}."


def build_morning_summary(today_count: int, overdue_count: int, inbox_count: int) -> str:
    parts = ["Доброе утро."]
    if today_count:
        parts.append(f"На сегодня запланировано {today_count} задач.")
    if overdue_count:
        parts.append(f"Просрочено ещё {overdue_count}.")
    if inbox_count:
        parts.append(f"Во входящих осталось {inbox_count} сообщений.")
    return " ".join(parts)


def build_evening_summary(done_count: int, open_count: int, inbox_count: int, tomorrow_count: int) -> str:
    parts = ["Под конец дня коротко:"]
    parts.append(f"сделано {done_count}")
    parts.append(f"осталось {open_count}")
    if inbox_count:
        parts.append(f"во входящих ещё {inbox_count}")
    if tomorrow_count:
        parts.append(f"на завтра уже есть {tomorrow_count}")
    return ", ".join(parts) + "."
