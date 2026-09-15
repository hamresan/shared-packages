"""Meta provider implementation for Instagram customer profile reads."""

from instagram_api.application.contracts.customer_profiles import (
    InstagramCustomerProfileProvider,
)
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramCustomerProfile,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaHttpMethod, MetaJsonExecutor

from .mapper import MetaInstagramCustomerProfileMapper
from .parser import MetaInstagramCustomerProfilePayloadParser

CUSTOMER_PROFILE_FIELDS = (
    "id",
    "name",
    "username",
    "profile_pic",
)


class MetaInstagramCustomerProfileProvider(InstagramCustomerProfileProvider):
    """Reads Instagram-scoped customer profiles through Meta infrastructure."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramCustomerProfilePayloadParser,
        mapper: MetaInstagramCustomerProfileMapper,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._mapper = mapper

    async def get_customer_profile(
        self,
        connection_id: InstagramConnectionId,
        user_id: InstagramUserId,
    ) -> InstagramCustomerProfile:
        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path=str(user_id),
            params={"fields": ",".join(CUSTOMER_PROFILE_FIELDS)},
        )
        dto = self._parser.parse(payload)
        return self._mapper.to_domain(dto)
