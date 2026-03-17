from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserOut(ORMModel):
    id: int
    telegram_user_id: int
    telegram_username: str | None
    first_name: str | None
    timezone: str


class TaskOut(ORMModel):
    id: int
    title: str
    description: str | None
    normalized_source_text: str | None
    due_date: date | None
    due_time: time | None
    due_at: datetime | None
    reminder_at: datetime | None
    is_done: bool
    list_id: int | None
    source_kind: str | None
    created_at: datetime


class TaskListOut(ORMModel):
    id: int
    title: str
    description: str | None
    normalized_source_text: str | None
    created_at: datetime
    updated_at: datetime


class InboxItemOut(ORMModel):
    id: int
    source_kind: str
    raw_text: str | None
    extracted_text: str | None
    normalized_text: str | None
    ai_summary: str | None
    ai_detected_type: str | None
    ai_confidence: float | None
    status: str
    processing_status: str
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
