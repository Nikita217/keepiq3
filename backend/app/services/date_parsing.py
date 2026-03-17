from __future__ import annotations

from datetime import date, datetime, timedelta

import dateparser
from dateparser.search import search_dates

from app.core.clock import combine_user_datetime, now_utc, parse_hhmm
from app.core.config import get_settings

TIME_HINTS = {
    "утром": "09:00",
    "с утра": "09:00",
    "днем": "14:00",
    "после обеда": "15:00",
    "вечером": "19:00",
    "к вечеру": "19:00",
    "ночью": "22:00",
}

WEEKDAY_HINTS = {
    "в понедельник": "понедельник 10:00",
    "во вторник": "вторник 10:00",
    "в среду": "среда 10:00",
    "в четверг": "четверг 10:00",
    "в пятницу": "пятница 10:00",
    "в субботу": "суббота 10:00",
    "в воскресенье": "воскресенье 10:00",
}


class ParsedDateResult:
    def __init__(self, due_at: datetime | None, due_date: date | None, due_time: str | None, reminder_at: datetime | None):
        self.due_at = due_at
        self.due_date = due_date
        self.due_time = due_time
        self.reminder_at = reminder_at


class DateParsingService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def parse(self, text: str, timezone: str | None, source_kind: str = "text") -> ParsedDateResult:
        base_text = (text or "").lower().strip()
        if not base_text:
            return ParsedDateResult(None, None, None, None)

        normalized = base_text
        for hint, replacement in TIME_HINTS.items():
            normalized = normalized.replace(hint, replacement)
        for hint, replacement in WEEKDAY_HINTS.items():
            normalized = normalized.replace(hint, replacement)

        settings = {
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": now_utc(),
            "TIMEZONE": timezone or self.settings.default_timezone,
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DAY_OF_MONTH": "first",
            "DATE_ORDER": "DMY",
        }

        found = search_dates(normalized, languages=["ru", "en"], settings=settings)
        parsed_dt = found[0][1] if found else dateparser.parse(normalized, languages=["ru", "en"], settings=settings)
        if not parsed_dt:
            return ParsedDateResult(None, None, None, None)

        default_time = parse_hhmm(self.settings.default_date_time)
        explicit_time = any(token in normalized for token in [":", "утра", "вечера", "дня", "ночи", "am", "pm"])
        due_date = parsed_dt.date()
        due_time = parsed_dt.timetz().replace(tzinfo=None) if explicit_time else default_time
        due_at = combine_user_datetime(due_date, due_time, timezone)

        reminder_at = due_at
        if source_kind in {"ticket", "reservation", "booking", "event", "photo", "document"}:
            reminder_at = due_at - timedelta(hours=self.settings.event_reminder_hours_before)
        elif due_at - now_utc() > timedelta(hours=2):
            reminder_at = due_at - timedelta(hours=1)

        if reminder_at < now_utc():
            reminder_at = due_at

        due_time_str = due_time.strftime("%H:%M") if due_time else None
        return ParsedDateResult(due_at, due_date, due_time_str, reminder_at)
