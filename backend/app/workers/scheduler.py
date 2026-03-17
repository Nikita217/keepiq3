from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.keyboards import action_keyboard, reminder_keyboard
from app.bot.runtime import bot
from app.copy.templates import build_analysis_message
from app.core.logging import logger
from app.db.session import SessionLocal
from app.services.actions import ActionService
from app.services.ai_pipeline import AIProcessingService
from app.services.inbox import InboxService
from app.services.summaries import ReminderService, SummaryService
from app.services.tasks import TaskService

action_service = ActionService()
ai_service = AIProcessingService()
inbox_service = InboxService()
task_service = TaskService()
summary_service = SummaryService()
reminder_service = ReminderService()


async def process_retry_inbox() -> None:
    if not bot:
        return
    async with SessionLocal() as session:
        items = await inbox_service.get_retry_items(session)
        for item in items:
            user = item.user
            if not user:
                continue
            try:
                understanding, embedding = await ai_service.analyze(inbox_item=item, user=user)
                await inbox_service.apply_understanding(session, item=item, understanding=understanding, embedding=embedding)
                actions = await action_service.create_for_inbox(session, user=user, inbox_item=item, understanding=understanding)
                if item.telegram_chat_id:
                    response = await bot.send_message(item.telegram_chat_id, build_analysis_message(understanding, user.timezone), reply_markup=action_keyboard(actions))
                    for action in actions:
                        action.prompt_message_id = response.message_id
            except Exception as exc:  # noqa: BLE001
                await inbox_service.mark_processing_failed(session, item, str(exc))
                logger.warning("retry_inbox_failed", inbox_id=item.id, error=str(exc))
        await session.commit()


async def send_due_reminders() -> None:
    if not bot:
        return
    async with SessionLocal() as session:
        tasks = await task_service.due_reminders(session)
        for task in tasks:
            if not task.telegram_chat_id:
                continue
            await bot.send_message(task.telegram_chat_id, reminder_service.reminder_text(task), reply_markup=reminder_keyboard(task.id))
            await task_service.mark_reminder_sent(session, task)
        await session.commit()


async def send_morning_summaries() -> None:
    if not bot:
        return
    async with SessionLocal() as session:
        users = await summary_service.due_for_morning_summary(session)
        for user in users:
            text = await summary_service.build_morning_text(session, user)
            await bot.send_message(user.telegram_user_id, text)
            user.last_morning_summary_at = datetime.now(tz=timezone.utc)
        await session.commit()


async def send_evening_summaries() -> None:
    if not bot:
        return
    async with SessionLocal() as session:
        users = await summary_service.due_for_evening_summary(session)
        for user in users:
            text = await summary_service.build_evening_text(session, user)
            await bot.send_message(user.telegram_user_id, text)
            user.last_evening_summary_at = datetime.now(tz=timezone.utc)
        await session.commit()


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(process_retry_inbox, "interval", minutes=3, id="retry_inbox", max_instances=1, coalesce=True)
    scheduler.add_job(send_due_reminders, "interval", minutes=1, id="due_reminders", max_instances=1, coalesce=True)
    scheduler.add_job(send_morning_summaries, "interval", minutes=15, id="morning_summary", max_instances=1, coalesce=True)
    scheduler.add_job(send_evening_summaries, "interval", minutes=15, id="evening_summary", max_instances=1, coalesce=True)
    return scheduler
