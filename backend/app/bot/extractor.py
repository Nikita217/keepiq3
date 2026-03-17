from __future__ import annotations

import os
import tempfile
from pathlib import Path

from aiogram import Bot
from aiogram.types import Message

from app.services.media_extraction import MediaExtractionService


class TelegramMessageExtractor:
    def __init__(self) -> None:
        self.media_service = MediaExtractionService()

    async def extract(self, bot: Bot, message: Message) -> tuple[str, str | None, str | None]:
        if message.voice:
            raw_text = message.caption or ""
            extracted = await self._download_and_transcribe(bot, message.voice.file_id)
            return "voice", raw_text, extracted

        if message.photo:
            raw_text = message.caption or ""
            photo = message.photo[-1]
            extracted = await self._download_and_describe(bot, photo.file_id, raw_text)
            return "photo", raw_text, extracted

        if message.document and (message.document.mime_type or "").startswith("image/"):
            raw_text = message.caption or ""
            extracted = await self._download_and_describe(bot, message.document.file_id, raw_text)
            return "document", raw_text, extracted

        text = message.text or message.caption or ""
        if message.forward_origin:
            return "forwarded_message", text, text
        if "http://" in text or "https://" in text:
            return "link", text, text
        return "text", text, text

    async def _download_and_transcribe(self, bot: Bot, file_id: str) -> str:
        temp_path = await self._download_file(bot, file_id, suffix=".ogg")
        try:
            return await self.media_service.transcribe_audio(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def _download_and_describe(self, bot: Bot, file_id: str, caption: str | None) -> str:
        temp_path = await self._download_file(bot, file_id, suffix=".jpg")
        try:
            return await self.media_service.describe_image(temp_path, caption)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def _download_file(self, bot: Bot, file_id: str, suffix: str) -> str:
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, destination=temp_path)
        return temp_path
