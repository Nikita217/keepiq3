from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.schemas.task import TodayResponse
from app.services.tasks import TaskService

router = APIRouter()
service = TaskService()


@router.get("", response_model=TodayResponse)
async def get_today(user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> TodayResponse:
    overdue, today, inbox_count = await service.today_bucket(session, user)
    return TodayResponse(overdue=overdue, today=today, inbox_count=inbox_count)
