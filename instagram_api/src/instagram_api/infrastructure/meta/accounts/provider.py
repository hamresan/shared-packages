"""Meta provider implementation for Instagram account/profile reads."""

from instagram_api.application.contracts.accounts import InstagramAccountProvider
from instagram_api.domain import InstagramAccount, InstagramConnectionId
from instagram_api.infrastructure.meta.http import MetaHttpMethod, MetaRequestExecutor

from .mapper import MetaInstagramAccountMapper

ACCOUNT_PROFILE_FIELDS = (
    "id",
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
        executor: MetaRequestExecutor,
        mapper: MetaInstagramAccountMapper,
    ) -> None:
        self._executor = executor
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
        return self._mapper.to_domain(payload)
