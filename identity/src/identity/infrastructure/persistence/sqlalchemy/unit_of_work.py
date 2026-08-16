from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from identity.application.contracts.database import AsyncSessionFactory


class SqlAlchemyIdentityUnitOfWork:
    """Transaction boundary that obtains sessions exclusively from the host-provided factory."""

    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        session_iterator = self._session_factory()
        session = await anext(session_iterator)
        try:
            async with session.begin():
                yield session
        finally:
            await session.aclose()
            await session_iterator.aclose()
