"""In-memory unit of work for host-linking tests."""

from types import TracebackType
from typing import Self

from instagram_auth.application.contracts import (
    InstagramAuthUnitOfWork,
    InstagramConnectionRepository,
    InstagramCredentialRepository,
)
from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class FakeInstagramConnectionRepository(InstagramConnectionRepository):
    def __init__(self) -> None:
        self.connections: dict[InstagramConnectionId, InstagramConnection] = {}

    async def add(self, connection: InstagramConnection) -> None:
        self.connections[connection.id] = connection

    async def update(self, connection: InstagramConnection) -> None:
        self.connections[connection.id] = connection

    async def find_by_owner_and_account(
        self,
        *,
        owner_user_id: str,
        instagram_account_id: str,
    ) -> InstagramConnection | None:
        return next(
            (
                connection
                for connection in self.connections.values()
                if connection.owner_user_id == owner_user_id
                and connection.instagram_account_id == instagram_account_id
            ),
            None,
        )

    async def get_by_id(self, connection_id: InstagramConnectionId) -> InstagramConnection | None:
        return self.connections.get(connection_id)


class FakeInstagramCredentialRepository(InstagramCredentialRepository):
    def __init__(self) -> None:
        self.credentials: dict[InstagramConnectionId, InstagramProtectedCredential] = {}

    async def save(self, credential: InstagramProtectedCredential) -> None:
        self.credentials[credential.connection_id] = credential

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramProtectedCredential | None:
        return self.credentials.get(connection_id)


class FakeInstagramAuthUnitOfWork(InstagramAuthUnitOfWork):
    def __init__(self) -> None:
        self._connections = FakeInstagramConnectionRepository()
        self._credentials = FakeInstagramCredentialRepository()
        self.committed = False

    @property
    def connections(self) -> InstagramConnectionRepository:
        return self._connections

    @property
    def credentials(self) -> InstagramCredentialRepository:
        return self._credentials

    @property
    def connection_fake(self) -> FakeInstagramConnectionRepository:
        return self._connections

    @property
    def credential_fake(self) -> FakeInstagramCredentialRepository:
        return self._credentials

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
