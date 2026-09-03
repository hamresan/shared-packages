"""Async SQLAlchemy unit of work for Instagram authorization persistence."""

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from instagram_auth.application.contracts import (
    InstagramAuthUnitOfWork,
    InstagramConnectionRepository,
    InstagramCredentialRepository,
)
from instagram_auth.infrastructure.persistence.repositories import (
    SqlAlchemyInstagramConnectionRepository,
    SqlAlchemyInstagramCredentialRepository,
)


class SqlAlchemyInstagramAuthUnitOfWork(InstagramAuthUnitOfWork):
    """Create transaction-scoped repositories from an injected session factory."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._connections: InstagramConnectionRepository | None = None
        self._credentials: InstagramCredentialRepository | None = None

    @property
    def connections(self) -> InstagramConnectionRepository:
        if self._connections is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._connections

    @property
    def credentials(self) -> InstagramCredentialRepository:
        if self._credentials is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._credentials

    async def __aenter__(self) -> "SqlAlchemyInstagramAuthUnitOfWork":
        self._session = self._session_factory()
        self._connections = SqlAlchemyInstagramConnectionRepository(self._session)
        self._credentials = SqlAlchemyInstagramCredentialRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        session = self._require_session()
        if exc_type is not None:
            await session.rollback()
        await session.close()
        self._session = None
        self._connections = None
        self._credentials = None

    async def commit(self) -> None:
        await self._require_session().commit()

    async def rollback(self) -> None:
        await self._require_session().rollback()

    def _require_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._session
