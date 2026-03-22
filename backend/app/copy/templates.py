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


def build_analysis_message(understanding: StructuredUnderstanding, timezone_name: str | None = None) -> str:
    if understanding.detected_type == DetectedType.list:
        count = len(understanding.list_items)
        return f"Похоже, здесь список из {count} пунктов." if count else "Похоже, это список."
    if understanding.due_at_iso:
        dt = format_human_datetime(understanding.due_at, timezone_name)
        return f"Понял тебя. Похоже, это напоминание на {dt}."
    if understanding.detected_type == DetectedType.unclear:
        return "Я не до конца уверен, поэтому пока оставлю это ближе к входящим вариантам."
    return f"Понял тебя. Похоже, это задача: {understanding.title.strip()}"


def build_keep_inbox_message() -> str:
    return "Оставил это во входящих, чтобы не потерялось."


def build_task_saved_message(task: Task, timezone_name: str | None = None) -> str:
    if task.due_at:
        return f"Сохранил. Напомню {format_human_datetime(task.due_at, timezone_name)}."
    return "Сохранил как задачу без даты."


def build_list_saved_message(title: str, count: int) -> str:
    return f"Сохранил список «{title}». Внутри {count} пунктов."


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
