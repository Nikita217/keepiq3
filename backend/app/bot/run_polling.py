import asyncio

from app.bot.runtime import bot, delete_webhook, dp


async def main() -> None:
    if not bot:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")
    await delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
