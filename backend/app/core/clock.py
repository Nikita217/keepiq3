from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def user_tz(timezone_name: str | None) -> ZoneInfo:
    settings = get_settings()
    return ZoneInfo(timezone_name or settings.default_timezone)


def local_now(timezone_name: str | None) -> datetime:
    return now_utc().astimezone(user_tz(timezone_name))


def combine_user_datetime(day: date, at: time, timezone_name: str | None) -> datetime:
    localized = datetime.combine(day, at).replace(tzinfo=user_tz(timezone_name))
    return localized.astimezone(timezone.utc)


def parse_hhmm(value: str) -> time:
    hours, minutes = value.split(":")
    return time(hour=int(hours), minute=int(minutes))


def next_local_occurrence(hour_minute: str, timezone_name: str | None, base: datetime | None = None) -> datetime:
    base_local = (base or now_utc()).astimezone(user_tz(timezone_name))
    target_time = parse_hhmm(hour_minute)
    candidate = datetime.combine(base_local.date(), target_time).replace(tzinfo=base_local.tzinfo)
    if candidate <= base_local:
        candidate = candidate + timedelta(days=1)
    return candidate.astimezone(timezone.utc)
