from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, HTTPException, Request

from app.bot.handlers import router
from app.core.config import get_settings

settings = get_settings()

bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) if settings.telegram_bot_token else None
dp = Dispatcher()
dp.include_router(router)


async def handle_webhook(request: Request) -> dict[str, bool]:
    if not bot:
        raise HTTPException(status_code=500, detail="Telegram bot is not configured.")
    update = Update.model_validate(await request.json())
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}


async def configure_webhook(app: FastAPI) -> None:
    if not bot or not settings.telegram_use_webhook:
        return
    webhook_url = f"{settings.app_base_url.rstrip('/')}{settings.telegram_webhook_path}"
    await bot.set_webhook(webhook_url, secret_token=settings.telegram_webhook_secret)


async def delete_webhook() -> None:
    if bot:
        await bot.delete_webhook(drop_pending_updates=False)
