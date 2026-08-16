from types import TracebackType
from typing import Protocol, Self

from identity.application.contracts.repositories import (
    OtpChallengeRepository,
    SessionRepository,
    UserIdentityRepository,
    UserRepository,
)


class IdentityUnitOfWork(Protocol):
    @property
    def users(self) -> UserRepository: ...

    @property
    def identities(self) -> UserIdentityRepository: ...

    @property
    def otp_challenges(self) -> OtpChallengeRepository: ...

    @property
    def sessions(self) -> SessionRepository: ...

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
