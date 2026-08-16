from types import TracebackType
from typing import Protocol, Self

from identity.application.contracts.repositories import (
    OtpChallengeRepository,
    SessionRepository,
    UserIdentityRepository,
    UserRepository,
)


class IdentityUnitOfWork(Protocol):
    users: UserRepository
    identities: UserIdentityRepository
    otp_challenges: OtpChallengeRepository
    sessions: SessionRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...


class IdentityUnitOfWorkFactory(Protocol):
    def __call__(self) -> IdentityUnitOfWork: ...
