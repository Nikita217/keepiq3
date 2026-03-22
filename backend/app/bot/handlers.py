from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.ai.fallback import heuristic_understanding
from app.ai.schemas import StructuredUnderstanding
from app.bot.extractor import TelegramMessageExtractor
from app.bot.keyboards import action_keyboard, mini_app_keyboard
from app.copy.templates import (
    build_analysis_message,
    build_keep_inbox_message,
    build_list_saved_message,
    build_task_saved_message,
    build_tasks_split_message,
)
from app.db.session import SessionLocal
from app.services.actions import ActionService
from app.services.ai_pipeline import AIProcessingService
from app.services.inbox import InboxService
from app.services.tasks import TaskService
from app.services.understanding_normalizer import normalize_understanding
from app.services.users import UserService

router = Router()
user_service = UserService()
inbox_service = InboxService()
ai_service = AIProcessingService()
action_service = ActionService()
task_service = TaskService()
extractor = TelegramMessageExtractor()


@router.message(CommandStart())
async def start(message: Message) -> None:
    text = (
        "Сюда можно присылать текст, голосовые, скрины, ссылки и пересланные сообщения. "
        "Я разберу это, пойму задачу или список и предложу сохранить в нужном виде."
    )
    await message.answer(text, reply_markup=mini_app_keyboard())


@router.message()
async def handle_incoming(message: Message) -> None:
    if not message.from_user:
        return

    async with SessionLocal() as session:
        user = await user_service.get_or_create_telegram_user(
            session,
            telegram_user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        source_kind, raw_text, extracted_text = await extractor.extract(message.bot, message)
        inbox_item = await inbox_service.create(
            session,
            user=user,
            source_kind=source_kind,
            raw_text=raw_text,
            extracted_text=extracted_text,
            telegram_chat_id=message.chat.id,
            telegram_message_id=message.message_id,
        )
        await session.commit()

    async with SessionLocal() as session:
        user = await user_service.get_or_create_telegram_user(
            session,
            telegram_user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        inbox_item = await inbox_service.get_by_id(session, user.id, inbox_item.id)
        if not inbox_item:
            return
        try:
            understanding, embedding = await ai_service.analyze(inbox_item=inbox_item, user=user)
            await inbox_service.apply_understanding(session, item=inbox_item, understanding=understanding, embedding=embedding)
            actions = await action_service.create_for_inbox(session, user=user, inbox_item=inbox_item, understanding=understanding)
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await inbox_service.mark_processing_failed(session, inbox_item, str(exc))
            await session.commit()
            await message.answer("Сохранил это во входящих. С разбором сейчас заминка, но я не потеряю сообщение.")
            return

    response = await message.answer(build_analysis_message(understanding, user.timezone), reply_markup=action_keyboard(actions))
    async with SessionLocal() as session:
        for action in actions:
            db_action = await action_service.get_action(session, action.id, user.id)
            if db_action:
                db_action.prompt_message_id = response.message_id
        await session.commit()


@router.callback_query(F.data.startswith("act:"))
async def handle_action(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    action_id = callback.data.split(":", maxsplit=1)[1]

    async with SessionLocal() as session:
        user = await user_service.get_or_create_telegram_user(
            session,
            telegram_user_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
        action = await action_service.get_action(session, action_id, user.id)
        if not action or not action.inbox_item_id:
            await callback.answer("Эта кнопка уже неактуальна.", show_alert=False)
            return
        inbox_item = await inbox_service.get_by_id(session, user.id, action.inbox_item_id)
        if not inbox_item:
            await callback.answer("Не нашёл исходное сообщение.", show_alert=False)
            return

        source_text = inbox_item.extracted_text or inbox_item.raw_text or ""
        if inbox_item.ai_payload_json:
            stored_understanding = StructuredUnderstanding.model_validate(inbox_item.ai_payload_json)
            understanding = normalize_understanding(stored_understanding, source_text)
        else:
            understanding = heuristic_understanding(
                text=source_text,
                source_kind=inbox_item.source_kind,
                timezone=user.timezone,
            )

        result = await action_service.execute(session, user=user, action=action, understanding=understanding, inbox_item=inbox_item)
        await session.commit()

    try:
        await callback.message.delete()
    except Exception:  # noqa: BLE001
        pass

    if result["kind"] == "task":
        await callback.answer("Сохранил задачу.")
        await callback.message.answer(build_task_saved_message(result["task"], user.timezone))
    elif result["kind"] == "list":
        task_list = result["task_list"]
        count = len(understanding.list_items)
        await callback.answer("Сохранил список.")
        await callback.message.answer(build_list_saved_message(task_list.title, count))
    elif result["kind"] == "task_split":
        await callback.answer("Разбил на задачи.")
        await callback.message.answer(build_tasks_split_message(result["count"]))
    else:
        await callback.answer("Оставил во входящих.")
        await callback.message.answer(build_keep_inbox_message())


@router.callback_query(F.data.startswith("rem:"))
async def handle_reminder_action(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return
    _, task_id, action = callback.data.split(":")
    async with SessionLocal() as session:
        user = await user_service.get_or_create_telegram_user(
            session,
            telegram_user_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
        task = await task_service.get_for_user(session, user.id, int(task_id))
        if not task:
            await callback.answer("Задача уже недоступна.")
            return
        if action == "done":
            task.is_done = True
        else:
            await task_service.snooze(session, task, action, user.timezone)
        await session.commit()
    await callback.answer("Готово.")
