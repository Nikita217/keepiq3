import asyncio
from datetime import timedelta

from app.core.clock import now_utc
from app.models.task import Task
from app.models.user import User
from app.services.tasks import TaskService


def test_reminder_scheduling_logic(session_factory):
    async def scenario():
        async with session_factory() as session:
            user = User(telegram_user_id=111, telegram_username='tester', first_name='Test', timezone='Europe/Moscow')
            session.add(user)
            await session.flush()
            task = Task(user_id=user.id, title='Позвонить', reminder_at=now_utc() - timedelta(minutes=1), is_done=False)
            session.add(task)
            await session.commit()

            due = await TaskService().due_reminders(session)
            assert len(due) == 1

            await TaskService().snooze(session, task, 'plus_1_hour', user.timezone)
            assert task.reminder_at is not None
            assert task.reminder_at > now_utc()

    asyncio.run(scenario())
