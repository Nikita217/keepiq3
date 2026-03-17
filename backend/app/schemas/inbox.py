from pydantic import BaseModel

from app.schemas.common import InboxItemOut, TaskListOut, TaskOut


class InboxDecisionRequest(BaseModel):
    action: str


class InboxConvertToTaskRequest(BaseModel):
    title: str | None = None
    keep_inbox: bool = False


class InboxConvertToListRequest(BaseModel):
    title: str | None = None


class InboxUpdate(BaseModel):
    status: str | None = None
    normalized_text: str | None = None
    ai_summary: str | None = None


class InboxActionResult(BaseModel):
    inbox: InboxItemOut
    task: TaskOut | None = None
    task_list: TaskListOut | None = None
