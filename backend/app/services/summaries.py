from __future__ import annotations

from datetime import timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import combine_user_datetime, local_now, next_local_occurrence, now_utc, parse_hhmm
from app.core.config import get_settings
from app.copy.templates import build_evening_summary, build_morning_summary, build_reminder_message
from app.models.inbox_item import InboxItem
from app.models.task import Task
from app.models.user import User


class SummaryService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def due_for_morning_summary(self, session: AsyncSession) -> list[User]:
        now = now_utc()
        result = await session.execute(select(User).where(User.is_active.is_(True)))
        users = []
        for user in result.scalars().all():
            local = local_now(user.timezone)
            target = parse_hhmm(self.settings.morning_summary_time)
            if local.hour == target.hour and abs(local.minute - target.minute) <= 15:
                if not user.last_morning_summary_at or user.last_morning_summary_at.date() < local.date():
                    users.append(user)
        return users

    async def due_for_evening_summary(self, session: AsyncSession) -> list[User]:
        result = await session.execute(select(User).where(User.is_active.is_(True)))
        users = []
        for user in result.scalars().all():
            local = local_now(user.timezone)
            target = parse_hhmm(self.settings.evening_summary_time)
            if local.hour == target.hour and abs(local.minute - target.minute) <= 15:
                if not user.last_evening_summary_at or user.last_evening_summary_at.date() < local.date():
                    users.append(user)
        return users

    async def build_morning_text(self, session: AsyncSession, user: User) -> str:
        local = local_now(user.timezone)
        start = combine_user_datetime(local.date(), parse_hhmm("00:00"), user.timezone)
        end = start + timedelta(days=1)

        today = await session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user.id,
                Task.is_done.is_(False),
                or_(
                    and_(Task.due_at.is_not(None), Task.due_at >= start, Task.due_at < end),
                    and_(Task.due_at.is_(None), Task.due_date == local.date()),
                ),
            )
        )
        overdue = await session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user.id,
                Task.is_done.is_(False),
                Task.due_at.is_not(None),
                Task.due_at < start,
            )
        )
        inbox = await session.execute(
            select(func.count(InboxItem.id)).where(InboxItem.user_id == user.id, InboxItem.status.in_(["new", "kept_in_inbox"]))
        )
        return build_morning_summary(int(today.scalar_one()), int(overdue.scalar_one()), int(inbox.scalar_one()))

    async def build_evening_text(self, session: AsyncSession, user: User) -> str:
        local = local_now(user.timezone)
        start = combine_user_datetime(local.date(), parse_hhmm("00:00"), user.timezone)
        end = start + timedelta(days=1)
        tomorrow_start = end
        tomorrow_end = tomorrow_start + timedelta(days=1)

        done = await session.execute(select(func.count(Task.id)).where(Task.user_id == user.id, Task.completed_at >= start, Task.completed_at < end))
        open_tasks = await session.execute(select(func.count(Task.id)).where(Task.user_id == user.id, Task.is_done.is_(False)))
        inbox = await session.execute(select(func.count(InboxItem.id)).where(InboxItem.user_id == user.id, InboxItem.status.in_(["new", "kept_in_inbox"])))
        tomorrow = await session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user.id,
                Task.is_done.is_(False),
                Task.due_at.is_not(None),
                Task.due_at >= tomorrow_start,
                Task.due_at < tomorrow_end,
            )
        )
        return build_evening_summary(int(done.scalar_one()), int(open_tasks.scalar_one()), int(inbox.scalar_one()), int(tomorrow.scalar_one()))


class ReminderService:
    def reminder_text(self, task: Task) -> str:
        return build_reminder_message(task)
