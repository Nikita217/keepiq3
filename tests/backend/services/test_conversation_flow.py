import asyncio

from app.ai.schemas import StructuredUnderstanding
from app.models.inbox_item import InboxItem
from app.models.user import User
from app.services.action_templates import ActionTemplateService
from app.services.conversations import ConversationService


UNDERSTANDING_PAYLOAD = {
    'detected_type': 'task',
    'confidence': 0.92,
    'normalized_text': 'завтра купить кроссовки для бега',
    'short_summary': 'Купить кроссовки для бега завтра',
    'title': 'Купить кроссовки для бега',
    'assistant_reply': 'Понял, завтра тебе нужно купить кроссовки для бега.',
    'helpful_tips': ['Сразу зафиксируй бюджет и покрытие, для которого они нужны.'],
    'follow_up_question': 'Если хочешь, могу помочь подобрать критерии выбора.',
    'due_date': None,
    'due_time': None,
    'due_at_iso': None,
    'reminder_at_iso': None,
    'list_items': [],
    'suggestions': [
        {'action': 'save_task', 'label': 'Сохранить задачу'},
        {'action': 'continue_conversation', 'label': 'Обсудить дальше'},
    ],
    'reasoning_notes_internal': 'test',
}


def test_action_templates_offer_continue_and_keep(session_factory):
    understanding = StructuredUnderstanding.model_validate(UNDERSTANDING_PAYLOAD)

    actions = ActionTemplateService().build_actions(understanding, 'Europe/Moscow')
    action_kinds = [item['action_kind'] for item in actions]

    assert action_kinds[-1] == 'keep_in_inbox'
    assert 'continue_conversation' in action_kinds
    assert 'save_task' in action_kinds


def test_conversation_service_keeps_context(session_factory):
    async def scenario():
        async with session_factory() as session:
            user = User(telegram_user_id=777, telegram_username='runner', first_name='Run', timezone='Europe/Moscow')
            session.add(user)
            await session.flush()

            inbox = InboxItem(user_id=user.id, source_kind='text', raw_text='завтра купить кроссовки', extracted_text='завтра купить кроссовки')
            session.add(inbox)
            await session.flush()

            service = ConversationService()
            understanding = StructuredUnderstanding.model_validate(UNDERSTANDING_PAYLOAD)
            conversation = await service.start(session, user=user, inbox_item=inbox, understanding=understanding)
            context = service.build_prompt_context(conversation)

            assert conversation.status == 'active'
            assert context is not None
            assert 'Купить кроссовки для бега' in context
            assert 'завтра купить кроссовки' in context

            follow_up_inbox = InboxItem(user_id=user.id, source_kind='text', raw_text='бюджет до 10000', extracted_text='бюджет до 10000')
            session.add(follow_up_inbox)
            await session.flush()
            await service.record_turn(session, conversation=conversation, inbox_item=follow_up_inbox, understanding=understanding)
            await service.close_active(session, user.id)

            closed = await service.get_active_for_user(session, user.id)
            assert closed is None

    asyncio.run(scenario())
