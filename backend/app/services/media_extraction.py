from __future__ import annotations

import base64
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import logger


class MediaExtractionService:
    """Extracts text meaning from non-text Telegram payloads.

    The MVP keeps binary files only temporarily. If OpenAI is unavailable, the service degrades to captions and file names
    so the inbox item remains searchable and can be retried later by the worker.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    async def transcribe_audio(self, file_path: str) -> str:
        if not self.client:
            return ""
        try:
            with Path(file_path).open("rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=self.settings.openai_transcription_model,
                    file=audio_file,
                    language="ru",
                    prompt=(
                        "Это голосовое сообщение для личного задачника. "
                        "Сохраняй формулировки максимально близко к оригиналу. "
                        "Не теряй даты, время, списки, цены, адреса, имена, номера и количества."
                    ),
                )
            return getattr(response, "text", "") or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("audio_transcription_failed", error=str(exc), file_path=file_path)
            return ""

    async def describe_image(self, file_path: str, caption: str | None = None) -> str:
        if not self.client:
            return caption or ""
        try:
            encoded = base64.b64encode(Path(file_path).read_bytes()).decode("utf-8")
            response = await self.client.chat.completions.create(
                model=self.settings.openai_vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Ты помогаешь личному задачнику. Извлеки из изображения полезный текст и короткий смысл. "
                                    "Ответь обычным русским текстом, без JSON. Сохраняй списки построчно. "
                                    "Не теряй даты, время, цены, адреса, телефоны, имена, бренды, номера заказов и билетов. "
                                    "Если это похоже на чеклист, список покупок, бронь, билет, событие или напоминание, "
                                    "сделай это понятным в извлеченном тексте."
                                ),
                            },
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}},
                        ],
                    }
                ],
                temperature=0.1,
            )
            answer = response.choices[0].message.content or ""
            if caption:
                return f"{caption}\n{answer}".strip()
            return answer
        except Exception as exc:  # noqa: BLE001
            logger.warning("image_extraction_failed", error=str(exc), file_path=file_path)
            return caption or ""
