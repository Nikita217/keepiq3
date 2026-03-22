from __future__ import annotations

from app.ai.client import AIClient
from app.ai.schemas import StructuredUnderstanding
from app.models.inbox_item import InboxItem
from app.models.user import User
from app.services.date_parsing import DateParsingService
from app.services.understanding_normalizer import normalize_understanding


class AIProcessingService:
    """Runs the two-step pipeline: text extraction happens before this service, then LLM structuring is merged with backend date parsing."""

    def __init__(self) -> None:
        self.ai_client = AIClient()
        self.date_parser = DateParsingService()

    async def analyze(self, *, inbox_item: InboxItem, user: User) -> tuple[StructuredUnderstanding, list[float] | None]:
        merged_text = inbox_item.extracted_text or inbox_item.raw_text or ""
        understanding = await self.ai_client.understand(
            raw_text=inbox_item.raw_text or "",
            extracted_text=inbox_item.extracted_text or "",
            source_kind=inbox_item.source_kind,
            timezone=user.timezone,
        )

        parsed = self.date_parser.parse(merged_text, user.timezone, source_kind=inbox_item.source_kind)
        if parsed.due_at and not understanding.due_at_iso:
            understanding = understanding.model_copy(
                update={
                    "due_at_iso": parsed.due_at.isoformat(),
                    "due_date": parsed.due_date.isoformat() if parsed.due_date else None,
                    "due_time": parsed.due_time,
                    "reminder_at_iso": parsed.reminder_at.isoformat() if parsed.reminder_at else None,
                }
            )

        understanding = normalize_understanding(understanding, merged_text)
        embedding = await self.ai_client.embed(" ".join(filter(None, [understanding.title, understanding.short_summary, understanding.normalized_text])))
        return understanding, embedding
