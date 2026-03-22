import asyncio

from app.ai.schemas import StructuredUnderstanding
from app.models.user import User
from app.services.inbox import InboxService


def test_create_inbox_item_and_apply_understanding(session_factory):
    async def scenario():
        async with session_factory() as session:
            user = User(telegram_user_id=111, telegram_username='tester', first_name='Test', timezone='Europe/Moscow')
            session.add(user)
            await session.flush()
            service = InboxService()
            inbox = await service.create(
                session,
                user=user,
                source_kind='text',
                raw_text='купить батарейки',
                extracted_text='купить батарейки',
                telegram_chat_id=1,
                telegram_message_id=2,
            )
            understanding = StructuredUnderstanding.model_validate(
                {
                    'detected_type': 'task',
                    'confidence': 0.9,
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
                    'suggestions': [{'action': 'save_task', 'label': 'Сохранить как задачу'}],
                    'reasoning_notes_internal': 'test',
                }
            )

            await service.apply_understanding(session, item=inbox, understanding=understanding, embedding=[0.1, 0.2])
            await session.commit()
            assert inbox.id is not None
            assert inbox.ai_detected_type == 'task'
            assert inbox.processing_status == 'completed'

    asyncio.run(scenario())
