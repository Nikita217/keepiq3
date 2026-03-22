from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.schemas import DetectedType, StructuredUnderstanding
from app.models.inbox_item import InboxItem
from app.models.task_list import TaskList
from app.models.user import User


class TaskListService:
    async def create_from_understanding(
        self,
        session: AsyncSession,
        *,
        user: User,
        inbox_item: InboxItem,
        understanding: StructuredUnderstanding,
        title: str | None = None,
        create_items: bool = True,
    ) -> TaskList:
        task_list = TaskList(
            user_id=user.id,
            title=(title or understanding.title or "Новый список")[:255],
            description=understanding.short_summary,
            normalized_source_text=understanding.normalized_text,
            source_inbox_item_id=inbox_item.id,
            telegram_chat_id=inbox_item.telegram_chat_id,
            telegram_message_id=inbox_item.telegram_message_id,
            embedding=inbox_item.embedding,
        )
        session.add(task_list)
        await session.flush()

        if create_items and understanding.list_items:
            from app.services.tasks import TaskService

            task_service = TaskService()
            for item in understanding.list_items:
                item_understanding = understanding.model_copy(
                    update={
                        "detected_type": DetectedType.task,
                        "title": item.title,
                        "short_summary": item.description or item.title,
                        "assistant_reply": understanding.assistant_reply,
                        "helpful_tips": [],
                        "ignored_phrases_internal": [],
                        "normalized_text": item.title,
                        "due_date": None,
                        "due_time": None,
                        "due_at_iso": item.due_at_iso,
                        "reminder_at_iso": item.due_at_iso,
                        "list_items": [],
                        "suggestions": [],
                    }
                )
                await task_service.create_from_understanding(
                    session,
                    user=user,
                    inbox_item=inbox_item,
                    understanding=item_understanding,
                    list_id=task_list.id,
                )

        return task_list

    async def list_for_user(self, session: AsyncSession, user_id: int) -> list[TaskList]:
        result = await session.execute(
            select(TaskList).where(TaskList.user_id == user_id).order_by(TaskList.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, session: AsyncSession, user_id: int, list_id: int) -> TaskList | None:
        result = await session.execute(
            select(TaskList)
            .where(TaskList.id == list_id, TaskList.user_id == user_id)
            .options(selectinload(TaskList.tasks))
        )
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, task_list: TaskList, *, title: str | None, description: str | None) -> TaskList:
        if title is not None:
            task_list.title = title
        if description is not None:
            task_list.description = description
        await session.flush()
        return task_list
