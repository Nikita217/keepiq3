from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import StructuredUnderstanding
from app.core.clock import combine_user_datetime, local_now, next_local_occurrence, now_utc, parse_hhmm
from app.core.config import get_settings
from app.models.inbox_item import InboxItem
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def create_manual(self, session: AsyncSession, user: User, data: TaskCreate) -> Task:
        task = Task(
            user_id=user.id,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            due_time=data.due_time,
            due_at=data.due_at,
            reminder_at=data.reminder_at,
            list_id=data.list_id,
            source_inbox_item_id=data.source_inbox_item_id,
        )
        session.add(task)
        await session.flush()
        return task

    async def create_from_understanding(
        self,
        session: AsyncSession,
        *,
        user: User,
        inbox_item: InboxItem,
        understanding: StructuredUnderstanding,
        override_due_at: datetime | None = None,
        keep_date: bool = True,
        list_id: int | None = None,
        title: str | None = None,
    ) -> Task:
        due_at = override_due_at or (understanding.due_at if keep_date else None)
        due_date = due_at.date() if due_at else None
        due_time = due_at.timetz().replace(tzinfo=None) if due_at else None
        reminder_at = understanding.reminder_at if keep_date and understanding.reminder_at else due_at

        task = Task(
            user_id=user.id,
            title=(title or understanding.title)[:255],
            description=understanding.short_summary,
            normalized_source_text=understanding.normalized_text,
            due_date=due_date,
            due_time=due_time,
            due_at=due_at,
            reminder_at=reminder_at,
            list_id=list_id,
            source_inbox_item_id=inbox_item.id,
            source_kind=inbox_item.source_kind,
            telegram_chat_id=inbox_item.telegram_chat_id,
            telegram_message_id=inbox_item.telegram_message_id,
            embedding=inbox_item.embedding,
        )
        session.add(task)
        await session.flush()
        return task

    async def update(self, session: AsyncSession, task: Task, data: TaskUpdate) -> Task:
        payload = data.model_dump(exclude_unset=True)
        for field, value in payload.items():
            setattr(task, field, value)
        if payload.get("is_done") is True:
            task.completed_at = now_utc()
        elif payload.get("is_done") is False:
            task.completed_at = None
        await session.flush()
        return task

    async def get_for_user(self, session: AsyncSession, user_id: int, task_id: int) -> Task | None:
        result = await session.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
        return result.scalar_one_or_none()

    async def today_bucket(self, session: AsyncSession, user: User) -> tuple[list[Task], list[Task], int]:
        local = local_now(user.timezone)
        start = datetime.combine(local.date(), datetime.min.time(), tzinfo=local.tzinfo).astimezone(timezone.utc)
        end = start + timedelta(days=1)

        overdue_result = await session.execute(
            select(Task)
            .where(
                Task.user_id == user.id,
                Task.is_done.is_(False),
                Task.due_at.is_not(None),
                Task.due_at < start,
            )
            .order_by(Task.due_at.asc())
        )
        today_result = await session.execute(
            select(Task)
            .where(
                Task.user_id == user.id,
                Task.is_done.is_(False),
                or_(
                    and_(Task.due_at.is_not(None), Task.due_at >= start, Task.due_at < end),
                    and_(Task.due_at.is_(None), Task.due_date == local.date()),
                ),
            )
            .order_by(Task.due_at.asc().nullslast(), Task.created_at.asc())
        )
        inbox_count_result = await session.execute(
            select(func.count(InboxItem.id)).where(
                InboxItem.user_id == user.id,
                InboxItem.status.in_(["new", "kept_in_inbox"]),
            )
        )
        return (
            list(overdue_result.scalars().all()),
            list(today_result.scalars().all()),
            int(inbox_count_result.scalar_one()),
        )

    async def calendar_for_date(self, session: AsyncSession, user: User, day) -> list[Task]:
        local_start = combine_user_datetime(day, parse_hhmm("00:00"), user.timezone)
        local_end = local_start + timedelta(days=1)
        result = await session.execute(
            select(Task)
            .where(
                Task.user_id == user.id,
                or_(
                    and_(Task.due_at.is_not(None), Task.due_at >= local_start, Task.due_at < local_end),
                    and_(Task.due_at.is_(None), Task.due_date == day),
                ),
            )
            .order_by(Task.due_at.asc().nullslast(), Task.created_at.asc())
        )
        return list(result.scalars().all())

    async def due_reminders(self, session: AsyncSession, now: datetime | None = None, limit: int = 50) -> list[Task]:
        current = now or now_utc()
        result = await session.execute(
            select(Task)
            .where(Task.is_done.is_(False), Task.reminder_at.is_not(None), Task.reminder_at <= current)
            .order_by(Task.reminder_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_reminder_sent(self, session: AsyncSession, task: Task) -> None:
        task.reminder_at = None
        await session.flush()

    async def snooze(self, session: AsyncSession, task: Task, kind: str, timezone_name: str | None) -> Task:
        if kind == "plus_1_hour":
            task.reminder_at = now_utc() + timedelta(hours=1)
        elif kind == "today_evening":
            task.reminder_at = next_local_occurrence("19:00", timezone_name)
        else:
            task.reminder_at = next_local_occurrence("10:00", timezone_name)
        await session.flush()
        return task

