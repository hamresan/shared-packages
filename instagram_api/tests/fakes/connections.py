"""Connection-aware fakes for contract tests."""

from instagram_api.application.contracts.connection import (
    InstagramAccessTokenProvider,
    InstagramConnectionReader,
)
from instagram_api.domain import InstagramConnection, InstagramConnectionId


class FakeInstagramAccessTokenProvider(InstagramAccessTokenProvider):
    """Fake access-token provider keyed strictly by connection ID."""

    def __init__(self, tokens: dict[InstagramConnectionId, str]) -> None:
        self._tokens = tokens
        self.requested_connection_ids: list[InstagramConnectionId] = []

    async def get_access_token(self, connection_id: InstagramConnectionId) -> str:
        self.requested_connection_ids.append(connection_id)
        return self._tokens[connection_id]


class FakeInstagramConnectionReader(InstagramConnectionReader):
    """Fake connection reader keyed strictly by connection ID."""

    def __init__(self, connections: dict[InstagramConnectionId, InstagramConnection]) -> None:
        self._connections = connections

    async def get_connection(self, connection_id: InstagramConnectionId) -> InstagramConnection:
        return self._connections[connection_id]
