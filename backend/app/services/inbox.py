from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.schemas import StructuredUnderstanding
from app.models.inbox_item import InboxItem
from app.models.user import User


class InboxService:
    async def create(
        self,
        session: AsyncSession,
        *,
        user: User,
        source_kind: str,
        raw_text: str | None,
        extracted_text: str | None,
        telegram_chat_id: int | None,
        telegram_message_id: int | None,
    ) -> InboxItem:
        item = InboxItem(
            user_id=user.id,
            source_kind=source_kind,
            raw_text=raw_text,
            extracted_text=extracted_text,
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
            status="new",
            processing_status="pending",
        )
        session.add(item)
        await session.flush()
        return item

    async def apply_understanding(
        self,
        session: AsyncSession,
        *,
        item: InboxItem,
        understanding: StructuredUnderstanding,
        embedding: list[float] | None,
    ) -> InboxItem:
        item.normalized_text = understanding.normalized_text
        item.ai_summary = understanding.short_summary
        item.ai_detected_type = understanding.detected_type.value
        item.ai_confidence = understanding.confidence
        item.ai_payload_json = understanding.model_dump(mode="json")
        item.embedding = embedding
        item.processing_status = "completed"
        item.processing_error = None
        await session.flush()
        return item

    async def mark_processing_failed(self, session: AsyncSession, item: InboxItem, error: str) -> None:
        item.processing_status = "retry_needed"
        item.processing_error = error[:1000]
        await session.flush()

    async def keep_in_inbox(self, session: AsyncSession, item: InboxItem) -> InboxItem:
        item.status = "kept_in_inbox"
        await session.flush()
        return item

    async def mark_converted(self, session: AsyncSession, item: InboxItem, target: str) -> InboxItem:
        item.status = f"converted_to_{target}"
        await session.flush()
        return item

    async def list_for_user(self, session: AsyncSession, user_id: int) -> list[InboxItem]:
        result = await session.execute(
            select(InboxItem)
            .where(InboxItem.user_id == user_id, InboxItem.status.in_(["new", "kept_in_inbox"]))
            .order_by(InboxItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, session: AsyncSession, user_id: int, inbox_id: int) -> InboxItem | None:
        result = await session.execute(
            select(InboxItem).where(InboxItem.id == inbox_id, InboxItem.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_retry_items(self, session: AsyncSession, limit: int = 20) -> list[InboxItem]:
        result = await session.execute(
            select(InboxItem)
            .where(InboxItem.processing_status.in_(["pending", "retry_needed"]))
            .options(selectinload(InboxItem.user))
            .order_by(InboxItem.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def clear_actions(self, session: AsyncSession, inbox_id: int) -> None:
        from app.models.bot_action import BotAction

        await session.execute(delete(BotAction).where(BotAction.inbox_item_id == inbox_id, BotAction.consumed_at.is_(None)))
