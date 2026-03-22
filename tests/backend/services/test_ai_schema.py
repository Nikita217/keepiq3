from app.ai.schemas import StructuredUnderstanding


def test_ai_schema_validation_deduplicates_suggestions_and_tips():
    payload = {
        "detected_type": "task",
        "confidence": 0.8,
        "normalized_text": "купить батарейки",
        "short_summary": "Купить батарейки",
        "title": "Купить батарейки",
        "assistant_reply": "Понял, нужно купить батарейки.",
        "helpful_tips": ["Проверь тип батареек заранее.", "Проверь тип батареек заранее."],
        "ignored_phrases_internal": ["привет", "привет"],
        "due_date": None,
        "due_time": None,
        "due_at_iso": None,
        "reminder_at_iso": None,
        "list_items": [],
        "suggestions": [
            {"action": "save_task", "label": "Сохранить как задачу"},
            {"action": "save_task", "label": "Повтор"},
            {"action": "save_task_without_date", "label": "Сохранить без даты"},
        ],
        "reasoning_notes_internal": "schema-test",
    }

    result = StructuredUnderstanding.model_validate(payload)

    assert result.detected_type.value == "task"
    assert len(result.suggestions) == 2
    assert result.helpful_tips == ["Проверь тип батареек заранее."]
    assert result.ignored_phrases_internal == ["привет"]
