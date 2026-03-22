from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.fallback import heuristic_understanding
from app.ai.schemas import StructuredUnderstanding
from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.schemas.inbox import InboxActionResult, InboxConvertToListRequest, InboxConvertToTaskRequest, InboxItemOut, InboxUpdate
from app.services.inbox import InboxService
from app.services.task_lists import TaskListService
from app.services.tasks import TaskService
from app.services.understanding_normalizer import normalize_understanding

router = APIRouter()
inbox_service = InboxService()
task_service = TaskService()
list_service = TaskListService()


def _understanding_for_item(item, timezone: str) -> StructuredUnderstanding:
    source_text = item.extracted_text or item.raw_text or ""
    if item.ai_payload_json:
        understanding = StructuredUnderstanding.model_validate(item.ai_payload_json)
        return normalize_understanding(understanding, source_text)
    return heuristic_understanding(text=source_text, source_kind=item.source_kind, timezone=timezone)


@router.get("", response_model=list[InboxItemOut])
async def get_inbox(user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> list[InboxItemOut]:
    return await inbox_service.list_for_user(session, user.id)


@router.patch("/{inbox_id}", response_model=InboxItemOut)
async def update_inbox(inbox_id: int, payload: InboxUpdate, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> InboxItemOut:
    item = await inbox_service.get_by_id(session, user.id, inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Входящее не найдено.")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(item, field, value)
    await session.commit()
    await session.refresh(item)
    return item


@router.post("/{inbox_id}/keep", response_model=InboxActionResult)
async def keep_in_inbox(inbox_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> InboxActionResult:
    item = await inbox_service.get_by_id(session, user.id, inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Входящее не найдено.")
    await inbox_service.keep_in_inbox(session, item)
    await session.commit()
    return InboxActionResult(inbox=item)


@router.post("/{inbox_id}/convert-task", response_model=InboxActionResult)
async def convert_to_task(inbox_id: int, payload: InboxConvertToTaskRequest, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> InboxActionResult:
    item = await inbox_service.get_by_id(session, user.id, inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Входящее не найдено.")
    understanding = _understanding_for_item(item, user.timezone)
    task = await task_service.create_from_understanding(
        session,
        user=user,
        inbox_item=item,
        understanding=understanding,
        keep_date=True,
        title=payload.title,
    )
    await inbox_service.mark_converted(session, item, "task")
    await session.commit()
    return InboxActionResult(inbox=item, task=task)


@router.post("/{inbox_id}/convert-list", response_model=InboxActionResult)
async def convert_to_list(inbox_id: int, payload: InboxConvertToListRequest, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> InboxActionResult:
    item = await inbox_service.get_by_id(session, user.id, inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Входящее не найдено.")
    understanding = _understanding_for_item(item, user.timezone)
    task_list = await list_service.create_from_understanding(
        session,
        user=user,
        inbox_item=item,
        understanding=understanding,
        title=payload.title,
    )
    await inbox_service.mark_converted(session, item, "list")
    await session.commit()
    return InboxActionResult(inbox=item, task_list=task_list)
