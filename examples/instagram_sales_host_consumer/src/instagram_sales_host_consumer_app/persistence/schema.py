"""Simple schema bootstrap for the example; production hosts own Alembic revisions."""

from sqlalchemy.ext.asyncio import AsyncEngine

from .models import host_metadata


class HostSchema:
    """Creates only host-owned example tables."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(host_metadata.create_all)
