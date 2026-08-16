from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from identity.application.contracts.database import AsyncSessionFactory
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyIdentityUnitOfWork:
    """Transaction boundary backed by the host-provided async session factory."""

    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_factory() as session, session.begin():
            yield session
