from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import StructuredUnderstanding
from app.core.config import get_settings
from app.models.bot_action import BotAction
from app.models.inbox_item import InboxItem
from app.models.user import User
from app.services.action_templates import ActionTemplateService
from app.services.conversations import ConversationService
from app.services.inbox import InboxService
from app.services.task_lists import TaskListService
from app.services.tasks import TaskService


class ActionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.templates = ActionTemplateService()
        self.inbox_service = InboxService()
        self.task_service = TaskService()
        self.task_list_service = TaskListService()
        self.conversation_service = ConversationService()

    async def create_for_inbox(
        self,
        session: AsyncSession,
        *,
        user: User,
        inbox_item: InboxItem,
        understanding: StructuredUnderstanding,
    ) -> list[BotAction]:
        await self.inbox_service.clear_actions(session, inbox_item.id)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=self.settings.callback_action_ttl_hours)
        actions = []
        for item in self.templates.build_actions(understanding, user.timezone):
            action = BotAction(
                user_id=user.id,
                inbox_item_id=inbox_item.id,
                action_kind=item["action_kind"],
                title=item["title"],
                payload=item["payload"],
                expires_at=expires_at,
            )
            session.add(action)
            actions.append(action)
        await session.flush()
        return actions

    async def get_action(self, session: AsyncSession, action_id: str, user_id: int) -> BotAction | None:
        result = await session.execute(
            select(BotAction).where(BotAction.id == action_id, BotAction.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def execute(
        self,
        session: AsyncSession,
        *,
        user: User,
        action: BotAction,
        understanding: StructuredUnderstanding,
        inbox_item: InboxItem,
    ) -> dict:
        action.consumed_at = datetime.now(tz=timezone.utc)

        if action.action_kind == "continue_conversation":
            conversation = await self.conversation_service.start(
                session,
                user=user,
                inbox_item=inbox_item,
                understanding=understanding,
            )
            return {"kind": "conversation", "conversation": conversation}

        await self.conversation_service.close_active(session, user.id)

        if action.action_kind == "keep_in_inbox":
            inbox = await self.inbox_service.keep_in_inbox(session, inbox_item)
            return {"kind": "inbox", "inbox": inbox}

        if action.action_kind == "save_list":
            task_list = await self.task_list_service.create_from_understanding(
                session,
                user=user,
                inbox_item=inbox_item,
                understanding=understanding,
                create_items=True,
            )
            await self.inbox_service.mark_converted(session, inbox_item, "list")
            return {"kind": "list", "task_list": task_list}

        if action.action_kind == "split_into_tasks":
            created_count = 0
            if understanding.list_items:
                for item in understanding.list_items:
                    split_understanding = understanding.model_copy(
                        update={
                            "title": item.title,
                            "short_summary": item.description or item.title,
                            "normalized_text": item.title,
                            "assistant_reply": understanding.assistant_reply,
                            "helpful_tips": [],
                            "follow_up_question": None,
                            "due_at_iso": item.due_at_iso,
                            "reminder_at_iso": item.due_at_iso,
                            "list_items": [],
                            "suggestions": [],
                        }
                    )
                    await self.task_service.create_from_understanding(
                        session,
                        user=user,
                        inbox_item=inbox_item,
                        understanding=split_understanding,
                    )
                    created_count += 1
            else:
                await self.task_service.create_from_understanding(
                    session,
                    user=user,
                    inbox_item=inbox_item,
                    understanding=understanding,
                )
                created_count = 1
            await self.inbox_service.mark_converted(session, inbox_item, "tasks")
            return {"kind": "task_split", "count": created_count}

        override_due_at = self.templates.resolve_due_at(action.action_kind, understanding, user.timezone)
        keep_date = action.action_kind != "save_task_without_date"
        task = await self.task_service.create_from_understanding(
            session,
            user=user,
            inbox_item=inbox_item,
            understanding=understanding,
            override_due_at=override_due_at,
            keep_date=keep_date,
        )
        await self.inbox_service.mark_converted(session, inbox_item, "task")
        return {"kind": "task", "task": task}
