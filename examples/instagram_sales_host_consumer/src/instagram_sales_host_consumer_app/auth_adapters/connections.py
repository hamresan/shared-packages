"""Adapter from instagram-auth connection reads to instagram-api connection reads."""

from uuid import UUID

from instagram_api.application.contracts import InstagramConnectionReader
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
)
from instagram_auth import (
    InstagramConnectionId as AuthInstagramConnectionId,
)
from instagram_auth import (
    InstagramConnectionReader as AuthInstagramConnectionReader,
)
from instagram_auth import InstagramConnectionState


class InstagramAuthConnectionAdapter(InstagramConnectionReader):
    """Adapts auth-owned connection state to the API-owned connection contract."""

    def __init__(self, reader: AuthInstagramConnectionReader) -> None:
        self._reader = reader

    async def get_connection(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection:
        auth_id = AuthInstagramConnectionId(UUID(str(connection_id)))
        connection = await self._reader.get(auth_id)
        if connection is None:
            raise LookupError(f"Instagram connection not found: {connection_id}")

        return InstagramConnection(
            id=connection_id,
            provider_account_id=InstagramAccountId(connection.instagram_account_id),
            permissions=frozenset(permission.value for permission in connection.permissions),
            is_usable=connection.status is InstagramConnectionState.CONNECTED,
        )
