"""Transaction boundary for Instagram authorization persistence."""

from types import TracebackType
from typing import Protocol, Self

from instagram_auth.application.contracts.connection_repository import InstagramConnectionRepository
from instagram_auth.application.contracts.credential_repository import InstagramCredentialRepository


class InstagramAuthUnitOfWork(Protocol):
    """Coordinate connection and credential persistence in one transaction."""

    @property
    def connections(self) -> InstagramConnectionRepository:
        """Return the transaction-scoped connection repository."""
        ...

    @property
    def credentials(self) -> InstagramCredentialRepository:
        """Return the transaction-scoped credential repository."""
        ...

    async def __aenter__(self) -> Self:
        """Open the transaction scope."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the transaction scope, rolling back on failure."""
        ...

    async def commit(self) -> None:
        """Commit the transaction."""
        ...

    async def rollback(self) -> None:
        """Roll back the transaction."""
        ...
