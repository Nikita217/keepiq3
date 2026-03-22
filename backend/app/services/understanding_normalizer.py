from __future__ import annotations

import re

from app.ai.schemas import DetectedType, ListItemCandidate, StructuredUnderstanding

GREETING_RE = re.compile(
    r"^(?:(?:привет(?:ик)?|здравствуй(?:те)?|добрый день|доброе утро|добрый вечер|хай|hello|hi|слушай|смотри|ну|так)\b[\s,!.:;-]*)+",
    re.IGNORECASE,
)
POLITE_RE = re.compile(
    r"^(?:(?:пожалуйста|плиз|если можешь|будь добр(?:а|ы)?)\b[\s,!.:;-]*)+",
    re.IGNORECASE,
)
COMMAND_RE = re.compile(
    r"^(?:(?:напомни(?:\s+мне)?|не забудь|запиши(?:\s+мне)?|сохрани|добавь|поставь(?:\s+задачу)?|создай(?:\s+задачу)?|запланируй|напоминание\s+про|мне\s+нужно|мне\s+надо|нужно|надо(?:\s+бы)?)\b[\s,!.:;-]*)+",
    re.IGNORECASE,
)
TEMPORAL_RE = re.compile(
    r"^(?:(?:сегодня|завтра|послезавтра|утром|вечером|ночью|днем|после обеда|к вечеру|на сегодня|на завтра|в понедельник|во вторник|в среду|в четверг|в пятницу|в субботу|в воскресенье|в\s+\d{1,2}(?::\d{2})?|к\s+\d{1,2}(?::\d{2})?)\b[\s,!.:;-]*)+",
    re.IGNORECASE,
)
MULTISPACE_RE = re.compile(r"\s+")
BULLET_PREFIX_RE = re.compile(r"^(?:(?:[-*•]|[—–])\s+|\d+[.)]\s+)+")
INLINE_SPLIT_RE = re.compile(r"\s*(?:,|;|•)\s*")
TRAILING_TIME_RE = re.compile(
    r"[\s,!.:;-]+(?:сегодня|завтра|послезавтра|утром|вечером|ночью|днем|после обеда|в\s+\d{1,2}(?::\d{2})?|к\s+\d{1,2}(?::\d{2})?)$",
    re.IGNORECASE,
)
TASK_SUMMARY_SERVICE_RE = re.compile(
    r"^(?:напоминани\w*|напомнить|задача(?:\s*:)?|пользователь\s+(?:хочет|просит)|нужно|надо)\b",
    re.IGNORECASE,
)
NOISE_VALUES = {
    "",
    "привет",
    "приветик",
    "пожалуйста",
    "напомни",
    "напомни мне",
    "сохрани",
    "добавь",
    "задача",
    "список",
}
DEFAULT_ASSISTANT_REPLY = "Понял, что это нужно сохранить."


def normalize_spaces(text: str) -> str:
    return MULTISPACE_RE.sub(" ", (text or "").replace("\r", "\n")).strip()


def normalize_multiline_text(text: str) -> str:
    value = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[^\S\n]+", " ", value)
    value = re.sub(r" *\n+ *", "\n", value)
    return value.strip()


def capitalize_sentence(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def _strip_repeated_prefixes(text: str) -> tuple[str, list[str]]:
    value = text
    ignored: list[str] = []
    changed = True
    patterns = (GREETING_RE, POLITE_RE, COMMAND_RE, TEMPORAL_RE)
    while changed and value:
        changed = False
        for pattern in patterns:
            match = pattern.match(value)
            if not match:
                continue
            fragment = match.group(0).strip(" ,.!:;-")
            if fragment:
                ignored.append(fragment)
            value = value[match.end():].strip(" ,.!:;-")
            changed = True
    return value, ignored


def clean_task_title(text: str) -> tuple[str, list[str]]:
    value = normalize_spaces(text)
    if not value:
        return "", []

    value = BULLET_PREFIX_RE.sub("", value)
    value, ignored = _strip_repeated_prefixes(value)
    value = re.sub(r"^(?:мне|для меня)\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(?:пожалуйста|плиз)\b", "", value, flags=re.IGNORECASE)
    value = TRAILING_TIME_RE.sub("", value).strip(" ,.!:;-")
    value = normalize_spaces(value)
    if value.lower() in NOISE_VALUES:
        return "", ignored
    return capitalize_sentence(value), ignored


def _split_candidate_parts(text: str) -> list[str]:
    normalized = normalize_multiline_text(text)
    if not normalized:
        return []

    parts: list[str] = []
    for line in normalized.split("\n"):
        cleaned_line = BULLET_PREFIX_RE.sub("", line).strip(" ,;")
        if not cleaned_line:
            continue
        inline_parts = [part for part in INLINE_SPLIT_RE.split(cleaned_line) if normalize_spaces(part)]
        if len(inline_parts) > 1:
            parts.extend(inline_parts)
        else:
            parts.append(cleaned_line)
    return parts


def detect_list_items(text: str) -> list[ListItemCandidate]:
    raw_parts = _split_candidate_parts(text)
    if len(raw_parts) < 2:
        return []

    items: list[ListItemCandidate] = []
    seen: set[str] = set()
    for part in raw_parts:
        cleaned, _ = clean_task_title(part)
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        items.append(ListItemCandidate(title=cleaned))
    return items


def _build_task_reply(title: str, has_date: bool) -> str:
    lowered = title[0].lower() + title[1:] if title else title
    if has_date:
        return f"Понял. Нужно {lowered}."
    return f"Похоже, это задача: {title}."


def _build_list_reply(title: str, items: list[ListItemCandidate]) -> str:
    preview = ", ".join(item.title for item in items[:3])
    if preview:
        return f"Понял. Это список «{title}». Сейчас вижу его так: {preview}."
    return f"Понял. Это список «{title}»."


def _list_title_from_items(items: list[ListItemCandidate], current_title: str) -> str:
    cleaned, _ = clean_task_title(current_title)
    if cleaned and cleaned.lower() not in {item.title.lower() for item in items}:
        return cleaned
    return "Список"


def _normalize_task_summary(summary: str, fallback: str) -> str:
    cleaned = normalize_spaces(summary)
    if not cleaned:
        return fallback
    lowered = cleaned.lower()
    if lowered.startswith("похоже") or "без точной даты" in lowered or TASK_SUMMARY_SERVICE_RE.match(cleaned):
        return fallback
    return cleaned[:300]


def _normalize_list_summary(summary: str, count: int) -> str:
    fallback = f"Список из {count} пунктов."
    cleaned = normalize_spaces(summary)
    if not cleaned:
        return fallback
    lowered = cleaned.lower()
    if lowered.startswith("похоже") or "несколько отдельных пунктов" in lowered:
        return fallback
    return cleaned[:300]


def normalize_understanding(understanding: StructuredUnderstanding, original_text: str) -> StructuredUnderstanding:
    source_text = normalize_spaces(original_text or understanding.normalized_text)
    normalized_text = normalize_spaces(understanding.normalized_text or source_text) or "Без текста"
    helper_items = detect_list_items(original_text or understanding.normalized_text)
    ignored_phrases: list[str] = []

    if understanding.detected_type == DetectedType.list:
        cleaned_items: list[ListItemCandidate] = []
        seen: set[str] = set()
        raw_items = understanding.list_items or helper_items
        for item in raw_items:
            cleaned_title, ignored = clean_task_title(item.title)
            ignored_phrases.extend(ignored)
            key = cleaned_title.lower()
            if not cleaned_title or key in seen:
                continue
            seen.add(key)
            cleaned_items.append(
                ListItemCandidate(
                    title=cleaned_title,
                    description=item.description,
                    due_at_iso=item.due_at_iso,
                )
            )

        if len(cleaned_items) <= 1:
            task_source = cleaned_items[0].title if cleaned_items else understanding.title or source_text
            task_title, ignored = clean_task_title(task_source)
            ignored_phrases.extend(ignored)
            task_title = task_title or capitalize_sentence(normalized_text[:255])
            return understanding.model_copy(
                update={
                    "detected_type": DetectedType.task,
                    "title": task_title[:255],
                    "short_summary": _normalize_task_summary(understanding.short_summary, task_title),
                    "assistant_reply": _build_task_reply(task_title, bool(understanding.due_at_iso or understanding.due_date)),
                    "normalized_text": normalized_text,
                    "list_items": [],
                    "ignored_phrases_internal": ignored_phrases[:6],
                }
            )

        list_title = _list_title_from_items(cleaned_items, understanding.title)
        return understanding.model_copy(
            update={
                "title": list_title[:255],
                "short_summary": _normalize_list_summary(understanding.short_summary, len(cleaned_items)),
                "assistant_reply": _build_list_reply(list_title, cleaned_items),
                "normalized_text": normalized_text,
                "list_items": cleaned_items,
                "ignored_phrases_internal": ignored_phrases[:6],
            }
        )

    cleaned_title, ignored = clean_task_title(understanding.title or source_text)
    ignored_phrases.extend(ignored)
    cleaned_title = cleaned_title or capitalize_sentence(normalized_text[:255])
    assistant_reply = normalize_spaces(understanding.assistant_reply)
    if not assistant_reply or assistant_reply == DEFAULT_ASSISTANT_REPLY or assistant_reply.lower().startswith("похоже"):
        assistant_reply = _build_task_reply(cleaned_title, bool(understanding.due_at_iso or understanding.due_date))
    return understanding.model_copy(
        update={
            "title": cleaned_title[:255],
            "short_summary": _normalize_task_summary(understanding.short_summary, cleaned_title),
            "assistant_reply": assistant_reply,
            "normalized_text": normalized_text,
            "ignored_phrases_internal": ignored_phrases[:6],
        }
    )
