import asyncio

from app.ai.schemas import StructuredUnderstanding
from app.models.inbox_item import InboxItem
from app.models.user import User
from app.services.task_lists import TaskListService
from app.services.tasks import TaskService


def test_convert_inbox_to_task(session_factory):
    async def scenario():
        async with session_factory() as session:
            user = User(telegram_user_id=111, telegram_username='tester', first_name='Test', timezone='Europe/Moscow')
            session.add(user)
            await session.flush()
            inbox = InboxItem(user_id=user.id, source_kind='text', raw_text='купить батарейки', extracted_text='купить батарейки')
            session.add(inbox)
            await session.flush()

            understanding = StructuredUnderstanding.model_validate(
                {
                    'detected_type': 'task',
                    'confidence': 0.8,
                    'normalized_text': 'купить батарейки',
                    'short_summary': 'Купить батарейки',
                    'title': 'Купить батарейки',
                    'assistant_reply': 'Понял, нужно купить батарейки.',
                    'helpful_tips': [],
                    'ignored_phrases_internal': [],
                    'due_date': None,
                    'due_time': None,
                    'due_at_iso': None,
                    'reminder_at_iso': None,
                    'list_items': [],
                    'suggestions': [],
                    'reasoning_notes_internal': 'test',
                }
            )

            task = await TaskService().create_from_understanding(session, user=user, inbox_item=inbox, understanding=understanding)
            await session.commit()
            assert task.title == 'Купить батарейки'
            assert task.source_inbox_item_id == inbox.id

    asyncio.run(scenario())


def test_convert_inbox_to_list_creates_list_items(session_factory):
    async def scenario():
        async with session_factory() as session:
            user = User(telegram_user_id=112, telegram_username='tester2', first_name='Test', timezone='Europe/Moscow')
            session.add(user)
            await session.flush()
            inbox = InboxItem(user_id=user.id, source_kind='voice', raw_text='купить молоко, заказать торт, позвать гостей', extracted_text='купить молоко, заказать торт, позвать гостей')
            session.add(inbox)
            await session.flush()

            understanding = StructuredUnderstanding.model_validate(
                {
                    'detected_type': 'list',
                    'confidence': 0.9,
                    'normalized_text': 'купить молоко, заказать торт, позвать гостей',
                    'short_summary': 'Список дел на праздник',
                    'title': 'Подготовка к празднику',
                    'assistant_reply': 'Понял, это список дел.',
                    'helpful_tips': [],
                    'ignored_phrases_internal': [],
                    'due_date': None,
                    'due_time': None,
                    'due_at_iso': None,
                    'reminder_at_iso': None,
                    'list_items': [
                        {'title': 'Купить молоко', 'description': None, 'due_at_iso': None},
                        {'title': 'Заказать торт', 'description': None, 'due_at_iso': None},
                    ],
                    'suggestions': [],
                    'reasoning_notes_internal': 'test',
                }
            )

            service = TaskListService()
            task_list = await service.create_from_understanding(session, user=user, inbox_item=inbox, understanding=understanding)
            await session.commit()
            detailed = await service.get_for_user(session, user.id, task_list.id)
            assert detailed is not None
            assert detailed.title == 'Подготовка к празднику'
            assert detailed.source_inbox_item_id == inbox.id
            assert len(detailed.tasks) == 2

    asyncio.run(scenario())
