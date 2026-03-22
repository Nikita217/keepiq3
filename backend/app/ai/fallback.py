from __future__ import annotations

from app.ai.schemas import DetectedType, ListItemCandidate, StructuredUnderstanding, Suggestion, SuggestionAction


def heuristic_understanding(*, text: str, source_kind: str, timezone: str | None) -> StructuredUnderstanding:
    normalized = " ".join((text or "").split()) or "Без текста"
    parts = [part.strip("-• ").strip() for part in normalized.replace("\r", "\n").split("\n") if part.strip()]
    comma_parts = [part.strip() for part in normalized.split(",") if len(part.strip()) > 2]
    list_candidates = parts if len(parts) > 1 else comma_parts

    if len(list_candidates) >= 3:
        items = [ListItemCandidate(title=item[:255]) for item in list_candidates[:12]]
        return StructuredUnderstanding(
            detected_type=DetectedType.list,
            confidence=0.56,
            normalized_text=normalized,
            short_summary=f"Похоже на список из {len(items)} пунктов.",
            title=(items[0].title if items else "Новый список"),
            list_items=items,
            suggestions=[
                Suggestion(action=SuggestionAction.save_list, label=f"Создать список из {len(items)} пунктов"),
                Suggestion(action=SuggestionAction.split_into_tasks, label=f"Разбить на {len(items)} задач"),
                Suggestion(action=SuggestionAction.save_task, label="Сохранить первой задачей"),
            ],
            reasoning_notes_internal=f"fallback:list:{source_kind}",
        )

    return StructuredUnderstanding(
        detected_type=DetectedType.task,
        confidence=0.45,
        normalized_text=normalized,
        short_summary="Похоже на одну задачу без точной даты.",
        title=normalized[:255],
        list_items=[],
        suggestions=[
            Suggestion(action=SuggestionAction.save_task, label="Сохранить как задачу"),
            Suggestion(action=SuggestionAction.remind_tomorrow_10, label="Напомнить завтра в 10:00"),
            Suggestion(action=SuggestionAction.remind_today_evening, label="Напомнить сегодня вечером"),
        ],
        reasoning_notes_internal=f"fallback:task:{source_kind}:{timezone or 'default'}",
    )
