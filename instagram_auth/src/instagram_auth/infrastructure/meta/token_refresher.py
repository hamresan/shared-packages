"""Meta implementation of Instagram access-token refresh."""

from instagram_auth.application import InstagramAuthorizationGrant
from instagram_auth.application.contracts import InstagramAccessTokenRefresher

from .client import MetaInstagramOAuthClient
from .mappers import MetaAuthorizationGrantMapper


class MetaInstagramAccessTokenRefresher(InstagramAccessTokenRefresher):
    """Refresh Instagram access tokens through Meta's provider endpoint."""

    def __init__(
        self,
        *,
        client: MetaInstagramOAuthClient,
        grant_mapper: MetaAuthorizationGrantMapper,
    ) -> None:
        self._client = client
        self._grant_mapper = grant_mapper

    async def refresh_access_token(self, *, access_token: str) -> InstagramAuthorizationGrant:
        dto = await self._client.refresh_access_token(access_token=access_token)
        return self._grant_mapper.map(dto)
