"""Isolated SQLite test database; PostgreSQL cases use a separate real server."""

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from scheduling.infrastructure.persistence.sqlalchemy.migrations import scheduling_metadata


@pytest.fixture
async def sqlite_engine(tmp_path: object) -> AsyncIterator[AsyncEngine]:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'calendars.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(scheduling_metadata().create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def sqlite_session_factory(
    sqlite_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(sqlite_engine, expire_on_commit=False)
