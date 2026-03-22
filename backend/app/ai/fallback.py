from __future__ import annotations

from app.ai.schemas import DetectedType, StructuredUnderstanding, Suggestion, SuggestionAction
from app.services.understanding_normalizer import detect_list_items, normalize_understanding, normalize_spaces


BUYING_HINTS = ("куп", "кроссов", "обув", "одежд", "ноут", "телефон")


def heuristic_understanding(*, text: str, source_kind: str, timezone: str | None) -> StructuredUnderstanding:
    normalized = normalize_spaces(text) or "Без текста"
    list_items = detect_list_items(normalized)

    if len(list_items) >= 2:
        understanding = StructuredUnderstanding(
            detected_type=DetectedType.list,
            confidence=0.62,
            normalized_text=normalized,
            short_summary=f"Список из {len(list_items)} пунктов.",
            title="Список",
            assistant_reply="Похоже, это список из нескольких отдельных пунктов.",
            helpful_tips=[],
            ignored_phrases_internal=[],
            list_items=list_items,
            suggestions=[
                Suggestion(action=SuggestionAction.save_list, label=f"Сохранить список ({len(list_items)})"),
                Suggestion(action=SuggestionAction.split_into_tasks, label="Разбить на задачи"),
            ],
            reasoning_notes_internal=f"fallback:list:{source_kind}",
        )
        return normalize_understanding(understanding, normalized)

    tips: list[str] = []
    if any(hint in normalized.lower() for hint in BUYING_HINTS):
        tips.append("Если покупка не срочная, можно сразу уточнить бюджет или критерии выбора.")

    understanding = StructuredUnderstanding(
        detected_type=DetectedType.task,
        confidence=0.55,
        normalized_text=normalized,
        short_summary="Одна понятная задача без точной даты.",
        title=normalized[:255],
        assistant_reply="Похоже, это одна задача.",
        helpful_tips=tips,
        ignored_phrases_internal=[],
        list_items=[],
        suggestions=[
            Suggestion(action=SuggestionAction.save_task, label="Сохранить как задачу"),
            Suggestion(action=SuggestionAction.remind_tomorrow_10, label="Поставить на завтра"),
            Suggestion(action=SuggestionAction.save_task_without_date, label="Сохранить без даты"),
        ],
        reasoning_notes_internal=f"fallback:task:{source_kind}:{timezone or 'default'}",
    )
    return normalize_understanding(understanding, normalized)
