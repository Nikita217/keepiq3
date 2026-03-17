from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.schemas.common import TaskListOut
from app.schemas.task_list import TaskListDetail, TaskListUpdate
from app.services.task_lists import TaskListService

router = APIRouter()
service = TaskListService()


@router.get("", response_model=list[TaskListOut])
async def get_lists(user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> list[TaskListOut]:
    return await service.list_for_user(session, user.id)


@router.get("/{list_id}", response_model=TaskListDetail)
async def get_list(list_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> TaskListDetail:
    task_list = await service.get_for_user(session, user.id, list_id)
    if not task_list:
        raise HTTPException(status_code=404, detail="Список не найден.")
    return TaskListDetail.model_validate(task_list)


@router.patch("/{list_id}", response_model=TaskListOut)
async def update_list(list_id: int, payload: TaskListUpdate, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> TaskListOut:
    task_list = await service.get_for_user(session, user.id, list_id)
    if not task_list:
        raise HTTPException(status_code=404, detail="Список не найден.")
    updated = await service.update(session, task_list, title=payload.title, description=payload.description)
    await session.commit()
    return updated
