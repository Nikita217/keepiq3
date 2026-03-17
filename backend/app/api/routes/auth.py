from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, validate_telegram_init_data
from app.db.session import get_db_session
from app.schemas.auth import TelegramAuthRequest
from app.schemas.common import AuthResponse, UserOut
from app.services.users import UserService

router = APIRouter()
user_service = UserService()
settings = get_settings()


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(payload: TelegramAuthRequest, session: AsyncSession = Depends(get_db_session)) -> AuthResponse:
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN is not configured.")
    telegram_user = validate_telegram_init_data(payload.init_data, settings.telegram_bot_token)
    user = await user_service.get_or_create_telegram_user(
        session,
        telegram_user_id=telegram_user["id"],
        username=telegram_user.get("username"),
        first_name=telegram_user.get("first_name"),
        last_name=telegram_user.get("last_name"),
    )
    await session.commit()
    token = create_access_token(subject=str(user.id), telegram_user_id=user.telegram_user_id)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/dev", response_model=AuthResponse)
async def dev_auth(session: AsyncSession = Depends(get_db_session)) -> AuthResponse:
    if not settings.allow_dev_auth:
        raise HTTPException(status_code=404, detail="Маршрут выключен.")
    user = await user_service.get_or_create_telegram_user(
        session,
        telegram_user_id=settings.dev_telegram_user_id,
        username=settings.dev_telegram_username,
        first_name=settings.dev_telegram_first_name,
        last_name=None,
    )
    await session.commit()
    token = create_access_token(subject=str(user.id), telegram_user_id=user.telegram_user_id)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))
