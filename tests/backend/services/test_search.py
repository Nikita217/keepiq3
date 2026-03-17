import asyncio

from app.models.inbox_item import InboxItem
from app.models.task import Task
from app.models.task_list import TaskList
from app.models.user import User
from app.search.service import SearchService


def test_search_returns_text_matches(session_factory):
    async def scenario():
        async with session_factory() as session:
            user = User(telegram_user_id=111, telegram_username='tester', first_name='Test', timezone='Europe/Moscow')
            session.add(user)
            await session.flush()
            session.add(Task(user_id=user.id, title='Купить корм коту', description='Взять влажный корм'))
            session.add(TaskList(user_id=user.id, title='День рождения', description='Торт и гости'))
            session.add(InboxItem(user_id=user.id, source_kind='text', raw_text='Билет на концерт', extracted_text='Билет на концерт'))
            await session.commit()

            results = await SearchService().search(session, user_id=user.id, query='концерт')
            assert results
            assert any(item.kind == 'inbox' for item in results)

    asyncio.run(scenario())
