"""Fakes for connection-management application tests."""

from types import TracebackType
from typing import Self

from instagram_auth.application.contracts import (
    InstagramAuthUnitOfWork,
    InstagramConnectionLister,
    InstagramConnectionReader,
    InstagramConnectionRepository,
    InstagramCredentialRepository,
)
from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class FakeConnectionStore(
    InstagramConnectionReader,
    InstagramConnectionLister,
    InstagramConnectionRepository,
):
    """In-memory connection store implementing Stage 7 boundaries explicitly."""

    def __init__(self, connections: tuple[InstagramConnection, ...] = ()) -> None:
        self.connections = {connection.id: connection for connection in connections}

    async def get(self, connection_id: InstagramConnectionId) -> InstagramConnection | None:
        return self.connections.get(connection_id)

    async def list_for_owner(self, owner_user_id: str) -> tuple[InstagramConnection, ...]:
        return tuple(
            connection
            for connection in self.connections.values()
            if connection.owner_user_id == owner_user_id
        )

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

    async def get_by_id(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        return self.connections.get(connection_id)


class FakeCredentialRepository(InstagramCredentialRepository):
    async def save(self, credential: InstagramProtectedCredential) -> None:
        del credential

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramProtectedCredential | None:
        del connection_id
        return None


class FakeInstagramAuthUnitOfWork(InstagramAuthUnitOfWork):
    def __init__(self, connections: FakeConnectionStore) -> None:
        self._connections = connections
        self._credentials = FakeCredentialRepository()
        self.commits = 0
        self.rollbacks = 0

    @property
    def connections(self) -> InstagramConnectionRepository:
        return self._connections

    @property
    def credentials(self) -> InstagramCredentialRepository:
        return self._credentials

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc, traceback
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1
