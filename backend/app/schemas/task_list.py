from pydantic import BaseModel, Field

from app.schemas.common import TaskListOut, TaskOut


class TaskListCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    source_inbox_item_id: int | None = None


class TaskListUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class TaskListDetail(TaskListOut):
    tasks: list[TaskOut]
