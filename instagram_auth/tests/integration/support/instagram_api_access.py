"""Cross-package support adapters using only public auth/API contracts."""

from collections.abc import Collection
from uuid import UUID

from instagram_api.application.contracts import (
    InstagramAccessTokenProvider as ApiAccessTokenProvider,
)
from instagram_api.application.contracts import (
    InstagramConnectionReader as ApiConnectionReader,
)
from instagram_api.domain import (
    InstagramAccountId,
)
from instagram_api.domain import (
    InstagramConnection as ApiInstagramConnection,
)
from instagram_api.domain import (
    InstagramConnectionId as ApiInstagramConnectionId,
)

from instagram_auth import (
    InstagramAccessTokenProvider as AuthAccessTokenProvider,
)
from instagram_auth import (
    InstagramConnection,
    InstagramConnectionId,
    InstagramConnectionReader,
    InstagramConnectionState,
    InstagramPermission,
)


class InMemoryAuthConnectionReader(InstagramConnectionReader):
    """Public-contract fake for cross-package integration tests."""

    def __init__(
        self,
        connections: dict[InstagramConnectionId, InstagramConnection],
    ) -> None:
        self._connections = connections

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        return self._connections.get(connection_id)


class InMemoryAuthAccessTokenProvider(AuthAccessTokenProvider):
    """Public-contract fake preserving explicit connection token isolation."""

    def __init__(self, tokens: dict[InstagramConnectionId, str]) -> None:
        self._tokens = tokens

    async def get_access_token(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> str:
        del required_permissions
        return self._tokens[connection_id]


class InstagramApiConnectionReaderAdapter(ApiConnectionReader):
    """Adapts auth-owned connection facts to the API-owned public contract."""

    def __init__(self, reader: InstagramConnectionReader) -> None:
        self._reader = reader

    async def get_connection(
        self,
        connection_id: ApiInstagramConnectionId,
    ) -> ApiInstagramConnection:
        auth_id = InstagramConnectionId(UUID(str(connection_id)))
        connection = await self._reader.get(auth_id)
        if connection is None:
            raise LookupError(f"Instagram connection not found: {connection_id}")

        return ApiInstagramConnection(
            id=connection_id,
            provider_account_id=InstagramAccountId(connection.instagram_account_id),
            permissions=frozenset(permission.value for permission in connection.permissions),
            is_usable=connection.status is InstagramConnectionState.CONNECTED,
        )


class InstagramApiAccessTokenAdapter(ApiAccessTokenProvider):
    """Adapts auth token access to the API-owned token contract."""

    def __init__(self, provider: AuthAccessTokenProvider) -> None:
        self._provider = provider

    async def get_access_token(
        self,
        connection_id: ApiInstagramConnectionId,
    ) -> str:
        return await self._provider.get_access_token(
            connection_id=InstagramConnectionId(UUID(str(connection_id)))
        )
