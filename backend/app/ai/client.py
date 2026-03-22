from __future__ import annotations

import json

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.ai.fallback import heuristic_understanding
from app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.ai.schemas import StructuredUnderstanding
from app.core.config import get_settings
from app.core.logging import logger


class AIClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    async def understand(
        self,
        *,
        raw_text: str,
        extracted_text: str,
        source_kind: str,
        timezone: str | None,
    ) -> StructuredUnderstanding:
        merged_text = extracted_text or raw_text or ""
        if not self.client:
            return heuristic_understanding(text=merged_text, source_kind=source_kind, timezone=timezone)

        schema = StructuredUnderstanding.model_json_schema()
        prompt = USER_PROMPT_TEMPLATE.format(
            timezone=timezone or self.settings.default_timezone,
            source_kind=source_kind,
            raw_text=raw_text or "",
            extracted_text=extracted_text or "",
            normalized_hint=merged_text,
            schema=json.dumps(schema, ensure_ascii=False),
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_reasoning_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            payload = json.loads(content)
            return StructuredUnderstanding.model_validate(payload)
        except (ValidationError, ValueError, IndexError) as exc:
            logger.warning("ai_understanding_invalid", error=str(exc))
            return heuristic_understanding(text=merged_text, source_kind=source_kind, timezone=timezone)
        except Exception as exc:  # noqa: BLE001
            logger.exception("ai_understanding_failed", error=str(exc))
            return heuristic_understanding(text=merged_text, source_kind=source_kind, timezone=timezone)

    async def embed(self, text: str) -> list[float] | None:
        if not self.client or not self.settings.search_embeddings_enabled or not text.strip():
            return None
        try:
            response = await self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=text[:8000],
            )
            return list(response.data[0].embedding)
        except Exception as exc:  # noqa: BLE001
            logger.warning("embedding_failed", error=str(exc))
            return None
