"""Public-contract fakes for hamresan-instagram-auth."""

from collections.abc import Collection

from instagram_auth import (
    InstagramAccessTokenProvider,
    InstagramConnection,
    InstagramConnectionId,
    InstagramConnectionReader,
    InstagramPermission,
)


class FakeAuthConnectionReader(InstagramConnectionReader):
    """Reads preconfigured auth-owned connection entities through the public contract."""

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


class FakeAuthAccessTokenProvider(InstagramAccessTokenProvider):
    """Returns a token only for the explicitly selected auth connection."""

    def __init__(self, tokens: dict[InstagramConnectionId, str]) -> None:
        self._tokens = tokens
        self.calls: list[InstagramConnectionId] = []

    async def get_access_token(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> str:
        del required_permissions
        self.calls.append(connection_id)
        return self._tokens[connection_id]
