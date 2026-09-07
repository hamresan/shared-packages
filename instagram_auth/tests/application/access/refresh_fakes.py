"""Fakes for Instagram credential refresh tests."""

from types import TracebackType
from typing import Self

from instagram_auth.application.contracts import (
    InstagramAccessTokenProvider,
    InstagramAccessTokenRefresher,
    InstagramAuthUnitOfWork,
    InstagramConnectionRepository,
    InstagramCredentialRepository,
)
from instagram_auth.application.models import (
    InstagramAuthorizationGrant,
    InstagramProtectedCredential,
)
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class FakeConnectionRepository(InstagramConnectionRepository):
    def __init__(self, connection: InstagramConnection) -> None:
        self.connection = connection
        self.updates: list[InstagramConnection] = []

    async def add(self, connection: InstagramConnection) -> None:
        self.connection = connection

    async def update(self, connection: InstagramConnection) -> None:
        self.connection = connection
        self.updates.append(connection)

    async def find_by_owner_and_account(
        self,
        *,
        owner_user_id: str,
        instagram_account_id: str,
    ) -> InstagramConnection | None:
        if (
            self.connection.owner_user_id == owner_user_id
            and self.connection.instagram_account_id == instagram_account_id
        ):
            return self.connection
        return None

    async def get_by_id(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        return self.connection if self.connection.id == connection_id else None


class FakeCredentialRepository(InstagramCredentialRepository):
    def __init__(self, credential: InstagramProtectedCredential) -> None:
        self.credential = credential
        self.saved: list[InstagramProtectedCredential] = []

    async def save(self, credential: InstagramProtectedCredential) -> None:
        self.credential = credential
        self.saved.append(credential)

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramProtectedCredential | None:
        return self.credential if self.credential.connection_id == connection_id else None


class FakeInstagramAuthUnitOfWork(InstagramAuthUnitOfWork):
    def __init__(
        self,
        *,
        connections: FakeConnectionRepository,
        credentials: FakeCredentialRepository,
    ) -> None:
        self._connections = connections
        self._credentials = credentials
        self.commits = 0

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
        return None

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        return None


class FakeAccessTokenRefresher(InstagramAccessTokenRefresher):
    def __init__(self, grant: InstagramAuthorizationGrant) -> None:
        self.grant = grant
        self.calls: list[str] = []

    async def refresh_access_token(self, *, access_token: str) -> InstagramAuthorizationGrant:
        self.calls.append(access_token)
        return self.grant


class FakeAccessTokenProvider(InstagramAccessTokenProvider):
    def __init__(self, token: str = "refreshed-token") -> None:
        self.token = token
        self.calls: list[InstagramConnectionId] = []

    async def get_access_token(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: tuple[InstagramPermission, ...] = (),
    ) -> str:
        del required_permissions
        self.calls.append(connection_id)
        return self.token
