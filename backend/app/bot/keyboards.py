from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import get_settings
from app.models.bot_action import BotAction

settings = get_settings()


def mini_app_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть KeepiQ", web_app=WebAppInfo(url=settings.telegram_mini_app_url))]
        ]
    )


def action_keyboard(actions: list[BotAction]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=action.title, callback_data=f"act:{action.id}")] for action in actions]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reminder_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выполнено", callback_data=f"rem:{task_id}:done")],
            [InlineKeyboardButton(text="Через 1 час", callback_data=f"rem:{task_id}:plus_1_hour")],
            [InlineKeyboardButton(text="Сегодня вечером", callback_data=f"rem:{task_id}:today_evening")],
            [InlineKeyboardButton(text="Завтра в 10:00", callback_data=f"rem:{task_id}:tomorrow_10")],
        ]
    )
