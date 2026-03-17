import asyncio
import sys
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / 'backend'
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.base import Base


@pytest.fixture()
def session_factory(tmp_path: Path):
    database_path = tmp_path / 'test.db'
    engine = create_async_engine(f'sqlite+aiosqlite:///{database_path}', future=True)

    async def setup() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(setup())
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    asyncio.run(engine.dispose())
