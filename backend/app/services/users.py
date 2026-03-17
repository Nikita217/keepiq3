from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserService:
    async def get_or_create_telegram_user(
        self,
        session: AsyncSession,
        *,
        telegram_user_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None = None,
        timezone: str = "Europe/Moscow",
    ) -> User:
        result = await session.execute(select(User).where(User.telegram_user_id == telegram_user_id))
        user = result.scalar_one_or_none()
        if user:
            user.telegram_username = username
            user.first_name = first_name
            user.last_name = last_name
            return user

        user = User(
            telegram_user_id=telegram_user_id,
            telegram_username=username,
            first_name=first_name,
            last_name=last_name,
            timezone=timezone,
        )
        session.add(user)
        await session.flush()
        return user
