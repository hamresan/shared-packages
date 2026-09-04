"""Reads Meta Instagram message details with historical-detail constraints."""

from instagram_api.domain import InstagramConnectionId, InstagramMessageId
from instagram_api.infrastructure.meta.http import MetaHttpMethod, MetaJsonExecutor, MetaProviderError

from .detail_policy import MetaInstagramMessageDetailAvailabilityPolicy
from .dto import MetaInstagramMessageDetailDto, MetaInstagramMessageSummaryDto
from .parser import MetaInstagramMessagingPayloadParser

MESSAGE_DETAIL_FIELDS = "id,created_time,from,to,message"


class MetaInstagramMessageDetailReader:
    """Reads a message detail when Meta still exposes it."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramMessagingPayloadParser,
        availability_policy: MetaInstagramMessageDetailAvailabilityPolicy,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._availability_policy = availability_policy

    async def read(
        self,
        connection_id: InstagramConnectionId,
        summary: MetaInstagramMessageSummaryDto,
    ) -> MetaInstagramMessageDetailDto | None:
        """Return message details or None when Meta does not expose them."""

        if summary.is_unsupported:
            return None

        try:
            payload = await self._executor.execute_json(
                connection_id=connection_id,
                method=MetaHttpMethod.GET,
                path=str(InstagramMessageId(summary.id)),
                params={"fields": MESSAGE_DETAIL_FIELDS},
            )
        except MetaProviderError as exc:
            if self._availability_policy.details_are_unavailable(exc):
                return None
            raise

        return self._parser.parse_message_detail(payload)
