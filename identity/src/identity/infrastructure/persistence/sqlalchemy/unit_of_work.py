from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self

from identity.application.contracts.database import AsyncSessionFactory
from identity.application.contracts.repositories import (
    ExternalIdentityRepository,
    OtpChallengeRepository,
    SessionRepository,
    UserIdentityRepository,
    UserRepository,
)
from identity.application.contracts.unit_of_work import IdentityUnitOfWork
from identity.infrastructure.persistence.sqlalchemy.mappers import (
    ExternalIdentityMapper,
    OtpChallengeMapper,
    SessionMapper,
    UserIdentityMapper,
    UserMapper,
)
from identity.infrastructure.persistence.sqlalchemy.repositories.external_identities import (
    SqlAlchemyExternalIdentityRepository,
)
from identity.infrastructure.persistence.sqlalchemy.repositories.otp_challenges import (
    SqlAlchemyOtpChallengeRepository,
)
from identity.infrastructure.persistence.sqlalchemy.repositories.sessions import (
    SqlAlchemySessionRepository,
)
from identity.infrastructure.persistence.sqlalchemy.repositories.user_identities import (
    SqlAlchemyUserIdentityRepository,
)
from identity.infrastructure.persistence.sqlalchemy.repositories.users import (
    SqlAlchemyUserRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyIdentityUnitOfWork(IdentityUnitOfWork):
    """SQLAlchemy unit of work backed by a host-provided session factory."""

    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory
        self._session_context: AbstractAsyncContextManager[AsyncSession] | None = None
        self._session: AsyncSession | None = None
        self._users: UserRepository | None = None
        self._identities: UserIdentityRepository | None = None
        self._external_identities: ExternalIdentityRepository | None = None
        self._otp_challenges: OtpChallengeRepository | None = None
        self._sessions: SessionRepository | None = None

    @property
    def users(self) -> UserRepository:
        if self._users is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._users

    @property
    def identities(self) -> UserIdentityRepository:
        if self._identities is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._identities

    @property
    def external_identities(self) -> ExternalIdentityRepository:
        if self._external_identities is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._external_identities

    @property
    def otp_challenges(self) -> OtpChallengeRepository:
        if self._otp_challenges is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._otp_challenges

    @property
    def sessions(self) -> SessionRepository:
        if self._sessions is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._sessions

    async def __aenter__(self) -> Self:
        self._session_context = self._session_factory()
        self._session = await self._session_context.__aenter__()
        self._users = SqlAlchemyUserRepository(self._session, UserMapper())
        self._identities = SqlAlchemyUserIdentityRepository(self._session, UserIdentityMapper())
        self._external_identities = SqlAlchemyExternalIdentityRepository(
            self._session,
            ExternalIdentityMapper(),
        )
        self._otp_challenges = SqlAlchemyOtpChallengeRepository(
            self._session,
            OtpChallengeMapper(),
        )
        self._sessions = SqlAlchemySessionRepository(self._session, SessionMapper())
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is not None and exc is not None:
            await self._session.rollback()
        if self._session_context is not None:
            await self._session_context.__aexit__(exc_type, exc, traceback)

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        await self._session.commit()


class SqlAlchemyIdentityUnitOfWorkFactory:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    def __call__(self) -> IdentityUnitOfWork:
        return SqlAlchemyIdentityUnitOfWork(self._session_factory)
