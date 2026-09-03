"""Meta implementation of the application authorization provider contract."""

from instagram_auth.application import InstagramAuthorizationGrant, InstagramAuthorizationProvider
from instagram_auth.domain import InstagramExternalIdentity

from .client import MetaInstagramOAuthClient
from .mappers import MetaAuthorizationGrantMapper, MetaExternalIdentityMapper


class MetaInstagramAuthorizationProvider(InstagramAuthorizationProvider):
    """Orchestrate Meta OAuth client calls and provider-to-domain mapping."""

    def __init__(
        self,
        client: MetaInstagramOAuthClient,
        grant_mapper: MetaAuthorizationGrantMapper,
        identity_mapper: MetaExternalIdentityMapper,
    ) -> None:
        self._client = client
        self._grant_mapper = grant_mapper
        self._identity_mapper = identity_mapper

    async def exchange_authorization_code(
        self,
        *,
        authorization_code: str,
        redirect_uri: str,
    ) -> InstagramAuthorizationGrant:
        dto = await self._client.exchange_authorization_code(
            authorization_code=authorization_code,
            redirect_uri=redirect_uri,
        )
        return self._grant_mapper.map(dto)

    async def resolve_external_identity(self, *, access_token: str) -> InstagramExternalIdentity:
        dto = await self._client.resolve_identity(access_token=access_token)
        return self._identity_mapper.map(dto)
