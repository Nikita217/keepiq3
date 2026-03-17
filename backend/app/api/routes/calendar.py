from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.schemas.common import TaskOut
from app.services.tasks import TaskService

router = APIRouter()
service = TaskService()


@router.get("", response_model=list[TaskOut])
async def tasks_for_date(date_value: date, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> list[TaskOut]:
    return await service.calendar_for_date(session, user, date_value)
