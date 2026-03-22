from app.ai.schemas import StructuredUnderstanding
from app.services.understanding_normalizer import detect_list_items, normalize_understanding


GREETING_PAYLOAD = {
    'detected_type': 'list',
    'confidence': 0.91,
    'normalized_text': 'Привет, напомни мне завтра купить молоко',
    'short_summary': 'Напоминание купить молоко',
    'title': 'Привет',
    'assistant_reply': 'Понял тебя.',
    'helpful_tips': [],
    'ignored_phrases_internal': [],
    'due_date': None,
    'due_time': None,
    'due_at_iso': None,
    'reminder_at_iso': None,
    'list_items': [
        {'title': 'Привет', 'description': None, 'due_at_iso': None},
        {'title': 'Напомни мне завтра купить молоко', 'description': None, 'due_at_iso': None},
    ],
    'suggestions': [
        {'action': 'save_list', 'label': 'Сохранить как список'},
    ],
    'reasoning_notes_internal': 'test',
}


def test_normalizer_reclassifies_greeting_list_to_task():
    understanding = StructuredUnderstanding.model_validate(GREETING_PAYLOAD)

    normalized = normalize_understanding(understanding, 'Привет, напомни мне завтра купить молоко')

    assert normalized.detected_type.value == 'task'
    assert normalized.title == 'Купить молоко'
    assert normalized.short_summary == 'Купить молоко'
    assert not normalized.list_items
    assert 'привет' in [item.lower() for item in normalized.ignored_phrases_internal]


def test_detect_list_items_ignores_greeting_noise():
    items = detect_list_items('Привет, напомни мне завтра купить молоко')

    assert len(items) == 1
    assert items[0].title == 'Купить молоко'


def test_detect_list_items_keeps_real_list():
    items = detect_list_items('молоко, яйца, сыр')

    assert [item.title for item in items] == ['Молоко', 'Яйца', 'Сыр']


def test_detect_list_items_from_bullets():
    items = detect_list_items('- молоко\n- яйца\n- сыр')

    assert [item.title for item in items] == ['Молоко', 'Яйца', 'Сыр']


def test_detect_list_items_does_not_split_hyphenated_words():
    items = detect_list_items('Проверить онлайн-оплату завтра')

    assert items == []
