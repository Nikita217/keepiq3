from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import StructuredUnderstanding
from app.models.conversation_session import ConversationSession
from app.models.inbox_item import InboxItem
from app.models.user import User


class ConversationService:
    async def get_active_for_user(self, session: AsyncSession, user_id: int) -> ConversationSession | None:
        result = await session.execute(
            select(ConversationSession)
            .where(ConversationSession.user_id == user_id, ConversationSession.status == "active")
            .order_by(ConversationSession.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def start(
        self,
        session: AsyncSession,
        *,
        user: User,
        inbox_item: InboxItem,
        understanding: StructuredUnderstanding,
    ) -> ConversationSession:
        conversation = await self.get_active_for_user(session, user.id)
        if conversation and conversation.last_inbox_item_id not in {None, inbox_item.id}:
            conversation.status = "closed"
            await session.flush()
            conversation = None

        if not conversation:
            conversation = ConversationSession(
                user_id=user.id,
                root_inbox_item_id=inbox_item.id,
                transcript_json=[],
                status="active",
            )
            session.add(conversation)
            await session.flush()
        await self.record_turn(session, conversation=conversation, inbox_item=inbox_item, understanding=understanding)
        return conversation

    async def record_turn(
        self,
        session: AsyncSession,
        *,
        conversation: ConversationSession,
        inbox_item: InboxItem,
        understanding: StructuredUnderstanding,
    ) -> ConversationSession:
        transcript = list(conversation.transcript_json or [])
        if conversation.last_inbox_item_id != inbox_item.id:
            user_text = (inbox_item.extracted_text or inbox_item.raw_text or "").strip()
            if user_text:
                transcript.append({"role": "user", "text": user_text[:1200]})
            transcript.append({"role": "assistant", "text": understanding.assistant_reply[:1200]})

        conversation.status = "active"
        conversation.last_inbox_item_id = inbox_item.id
        conversation.draft_kind = understanding.detected_type.value
        conversation.draft_title = understanding.title
        conversation.draft_summary = understanding.short_summary
        conversation.draft_payload_json = understanding.model_dump(mode="json")
        conversation.transcript_json = transcript[-10:]
        await session.flush()
        return conversation

    async def close_active(self, session: AsyncSession, user_id: int) -> None:
        conversation = await self.get_active_for_user(session, user_id)
        if not conversation:
            return
        conversation.status = "closed"
        await session.flush()

    def build_prompt_context(self, conversation: ConversationSession | None) -> str | None:
        if not conversation:
            return None

        parts: list[str] = []
        if conversation.draft_kind:
            parts.append(f"Current draft kind: {conversation.draft_kind}")
        if conversation.draft_title:
            parts.append(f"Current draft title: {conversation.draft_title}")
        if conversation.draft_summary:
            parts.append(f"Current draft summary: {conversation.draft_summary}")

        transcript = conversation.transcript_json or []
        if transcript:
            parts.append("Recent turns:")
            for turn in transcript[-6:]:
                role = turn.get("role", "assistant")
                text = (turn.get("text") or "").strip()
                if text:
                    parts.append(f"- {role}: {text}")

        return "\n".join(parts) if parts else None
