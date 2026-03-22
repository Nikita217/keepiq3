from app.ai.schemas import StructuredUnderstanding


def test_ai_schema_validation_deduplicates_suggestions():
    payload = {
        "detected_type": "task",
        "confidence": 0.8,
        "normalized_text": "купить батарейки",
        "short_summary": "Купить батарейки",
        "title": "Купить батарейки",
        "assistant_reply": "Понял, нужно купить батарейки.",
        "helpful_tips": ["Проверь тип батареек заранее.", "Проверь тип батареек заранее."],
        "follow_up_question": "Если хочешь, могу помочь уточнить модель.",
        "due_date": None,
        "due_time": None,
        "due_at_iso": None,
        "reminder_at_iso": None,
        "list_items": [],
        "suggestions": [
            {"action": "save_task", "label": "Сохранить как задачу"},
            {"action": "save_task", "label": "Повтор"},
            {"action": "continue_conversation", "label": "Обсудить дальше"},
        ],
        "reasoning_notes_internal": "schema-test",
    }

    result = StructuredUnderstanding.model_validate(payload)

    assert result.detected_type.value == "task"
    assert len(result.suggestions) == 2
    assert result.helpful_tips == ["Проверь тип батареек заранее."]
