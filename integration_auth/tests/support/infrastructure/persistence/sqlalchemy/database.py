"""Async SQLAlchemy test database support."""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from integration_auth.infrastructure.persistence.sqlalchemy.models.base import IntegrationAuthBase


class SqlAlchemyTestDatabase:
    """Create isolated SQLite persistence for integration tests."""

    def __init__(self, database_path: Path) -> None:
        self.engine: AsyncEngine = create_async_engine(
            f"sqlite+aiosqlite:///{database_path}",
            connect_args={"timeout": 5},
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(IntegrationAuthBase.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()
