import asyncio

from app.bot.runtime import bot
from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()
    if not bot:
        raise RuntimeError('TELEGRAM_BOT_TOKEN is not configured.')
    webhook_url = f"{settings.app_base_url.rstrip('/')}{settings.telegram_webhook_path}"
    await bot.set_webhook(webhook_url, secret_token=settings.telegram_webhook_secret)
    print(f'Webhook set to {webhook_url}')


if __name__ == '__main__':
    asyncio.run(main())
