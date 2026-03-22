from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class DetectedType(str, Enum):
    task = "task"
    list = "list"
    unclear = "unclear"


class SuggestionAction(str, Enum):
    save_task = "save_task"
    save_task_without_date = "save_task_without_date"
    save_list = "save_list"
    split_into_tasks = "split_into_tasks"
    remind_tomorrow_10 = "remind_tomorrow_10"
    remind_today_evening = "remind_today_evening"
    remind_at_detected_time = "remind_at_detected_time"
    continue_conversation = "continue_conversation"
    keep_in_inbox = "keep_in_inbox"


class Suggestion(BaseModel):
    action: SuggestionAction
    label: str = Field(min_length=2, max_length=80)


class ListItemCandidate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_at_iso: str | None = None


class StructuredUnderstanding(BaseModel):
    detected_type: DetectedType
    confidence: float = Field(ge=0.0, le=1.0)
    normalized_text: str = Field(min_length=1)
    short_summary: str = Field(min_length=1, max_length=300)
    title: str = Field(min_length=1, max_length=255)
    assistant_reply: str = Field(default="Понял, что это нужно сохранить.", min_length=1, max_length=500)
    helpful_tips: list[str] = Field(default_factory=list, min_length=0, max_length=2)
    follow_up_question: str | None = Field(default=None, max_length=200)
    due_date: str | None = None
    due_time: str | None = None
    due_at_iso: str | None = None
    reminder_at_iso: str | None = None
    list_items: list[ListItemCandidate] = Field(default_factory=list)
    suggestions: list[Suggestion] = Field(default_factory=list, min_length=0, max_length=3)
    reasoning_notes_internal: str = Field(default="", max_length=400)

    @field_validator("suggestions")
    @classmethod
    def unique_actions(cls, value: list[Suggestion]) -> list[Suggestion]:
        seen: set[str] = set()
        unique: list[Suggestion] = []
        for item in value:
            action_value = item.action.value
            if action_value not in seen:
                unique.append(item)
                seen.add(action_value)
        return unique[:3]

    @field_validator("helpful_tips")
    @classmethod
    def normalize_tips(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            cleaned = " ".join(item.split())
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(cleaned[:160])
        return normalized[:2]

    @property
    def due_at(self) -> datetime | None:
        return datetime.fromisoformat(self.due_at_iso) if self.due_at_iso else None

    @property
    def reminder_at(self) -> datetime | None:
        return datetime.fromisoformat(self.reminder_at_iso) if self.reminder_at_iso else None
