from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.schemas.common import TaskOut


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    due_time: time | None = None
    due_at: datetime | None = None
    reminder_at: datetime | None = None
    list_id: int | None = None
    source_inbox_item_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    due_time: time | None = None
    due_at: datetime | None = None
    reminder_at: datetime | None = None
    is_done: bool | None = None


class TaskSnoozeRequest(BaseModel):
    kind: str = Field(pattern="^(plus_1_hour|today_evening|tomorrow_10)$")


class TodayResponse(BaseModel):
    overdue: list[TaskOut]
    today: list[TaskOut]
    inbox_count: int
