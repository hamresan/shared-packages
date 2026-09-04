"""Schema lifecycle helper for optional SQLAlchemy webhook storage."""

from sqlalchemy.ext.asyncio import AsyncEngine

from .models import metadata


class SqlAlchemyInstagramWebhookSchema:
    """Creates the package-owned idempotency table when host migration tooling is absent."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create(self) -> None:
        """Create package-owned tables if they do not already exist."""

        async with self._engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
