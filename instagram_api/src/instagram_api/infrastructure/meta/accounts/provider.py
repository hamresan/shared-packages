"""Meta provider implementation for Instagram account/profile reads."""

from instagram_api.application.contracts.accounts import InstagramAccountProvider
from instagram_api.domain import InstagramAccount, InstagramConnectionId
from instagram_api.infrastructure.meta.http import MetaHttpMethod, MetaJsonExecutor

from .mapper import MetaInstagramAccountMapper
from .parser import MetaInstagramAccountPayloadParser

ACCOUNT_PROFILE_FIELDS = (
    "user_id",
    "username",
    "name",
    "biography",
    "website",
    "profile_picture_url",
    "followers_count",
    "follows_count",
    "media_count",
)


class MetaInstagramAccountProvider(InstagramAccountProvider):
    """Reads the selected professional account through Meta infrastructure."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramAccountPayloadParser,
        mapper: MetaInstagramAccountMapper,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._mapper = mapper

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path="me",
            params={"fields": ",".join(ACCOUNT_PROFILE_FIELDS)},
        )
        dto = self._parser.parse(payload)
        return self._mapper.to_domain(dto)
