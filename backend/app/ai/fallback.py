from __future__ import annotations

from app.ai.schemas import DetectedType, ListItemCandidate, StructuredUnderstanding, Suggestion, SuggestionAction


BUYING_HINTS = ("куп", "кроссов", "обув", "одежд", "ноут", "телефон")


def heuristic_understanding(*, text: str, source_kind: str, timezone: str | None) -> StructuredUnderstanding:
    normalized = " ".join((text or "").split()) or "Без текста"
    parts = [part.strip("-• ").strip() for part in normalized.replace("\r", "\n").split("\n") if part.strip()]
    comma_parts = [part.strip() for part in normalized.split(",") if len(part.strip()) > 2]
    list_candidates = parts if len(parts) > 1 else comma_parts

    if len(list_candidates) >= 2:
        items = [ListItemCandidate(title=item[:255]) for item in list_candidates[:12]]
        preview = "; ".join(item.title for item in items[:4])
        return StructuredUnderstanding(
            detected_type=DetectedType.list,
            confidence=0.62,
            normalized_text=normalized,
            short_summary=f"Список из {len(items)} пунктов.",
            title="Список" if len(items) < 2 else f"Список: {items[0].title[:40]}",
            assistant_reply=f"Похоже, это список. Сейчас вижу его так: {preview}.",
            helpful_tips=[],
            follow_up_question="Если хочешь, могу помочь уточнить список или разбить его по приоритету.",
            list_items=items,
            suggestions=[
                Suggestion(action=SuggestionAction.save_list, label=f"Сохранить список ({len(items)})"),
                Suggestion(action=SuggestionAction.continue_conversation, label="Уточнить список"),
                Suggestion(action=SuggestionAction.split_into_tasks, label="Разбить на задачи"),
            ],
            reasoning_notes_internal=f"fallback:list:{source_kind}",
        )

    tips: list[str] = []
    follow_up_question: str | None = None
    suggestions = [
        Suggestion(action=SuggestionAction.save_task, label="Сохранить как задачу"),
        Suggestion(action=SuggestionAction.remind_tomorrow_10, label="Поставить на завтра"),
    ]
    if any(hint in normalized.lower() for hint in BUYING_HINTS):
        tips.append("Если покупка не срочная, можно сразу уточнить бюджет и критерии выбора.")
        follow_up_question = "Если хочешь, могу помочь уточнить детали или подсказать, как выбрать вариант получше."
        suggestions.append(Suggestion(action=SuggestionAction.continue_conversation, label="Обсудить дальше"))
    else:
        suggestions.append(Suggestion(action=SuggestionAction.save_task_without_date, label="Сохранить без даты"))

    return StructuredUnderstanding(
        detected_type=DetectedType.task,
        confidence=0.55,
        normalized_text=normalized,
        short_summary="Одна понятная задача без точной даты.",
        title=normalized[:255],
        assistant_reply=f"Похоже, ты хочешь сохранить одну задачу: {normalized[:220]}.",
        helpful_tips=tips,
        follow_up_question=follow_up_question,
        list_items=[],
        suggestions=suggestions,
        reasoning_notes_internal=f"fallback:task:{source_kind}:{timezone or 'default'}",
    )
