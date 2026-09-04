"""Adapter from instagram-auth token access to instagram-api token access."""

from uuid import UUID

from instagram_api.application.contracts import InstagramAccessTokenProvider
from instagram_api.domain import InstagramConnectionId
from instagram_auth import InstagramAccessTokenProvider as AuthInstagramAccessTokenProvider
from instagram_auth import InstagramConnectionId as AuthInstagramConnectionId


class InstagramAuthAccessTokenAdapter(InstagramAccessTokenProvider):
    """Obtains provider access through the auth package's public boundary."""

    def __init__(self, provider: AuthInstagramAccessTokenProvider) -> None:
        self._provider = provider

    async def get_access_token(self, connection_id: InstagramConnectionId) -> str:
        return await self._provider.get_access_token(
            connection_id=AuthInstagramConnectionId(UUID(str(connection_id)))
        )
