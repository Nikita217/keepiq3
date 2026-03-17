import asyncio

from app.core.logging import configure_logging
from app.workers.scheduler import build_scheduler


async def main() -> None:
    configure_logging()
    scheduler = build_scheduler()
    scheduler.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
