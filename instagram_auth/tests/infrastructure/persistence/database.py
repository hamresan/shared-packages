from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from instagram_auth.infrastructure.persistence import InstagramAuthBase


async def build_database(path: Path) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async with engine.begin() as connection:
        await connection.run_sync(InstagramAuthBase.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)
