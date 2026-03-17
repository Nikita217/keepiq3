from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.schemas.common import TaskOut
from app.schemas.task import TaskCreate, TaskSnoozeRequest, TaskUpdate
from app.services.tasks import TaskService

router = APIRouter()
service = TaskService()


@router.post("", response_model=TaskOut)
async def create_task(payload: TaskCreate, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> TaskOut:
    task = await service.create_manual(session, user, payload)
    await session.commit()
    return task


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, payload: TaskUpdate, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> TaskOut:
    task = await service.get_for_user(session, user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    task = await service.update(session, task, payload)
    await session.commit()
    return task


@router.post("/{task_id}/snooze", response_model=TaskOut)
async def snooze_task(task_id: int, payload: TaskSnoozeRequest, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> TaskOut:
    task = await service.get_for_user(session, user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    task = await service.snooze(session, task, payload.kind, user.timezone)
    await session.commit()
    return task
