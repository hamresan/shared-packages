"""Reads Meta Instagram message details within documented limits."""

from instagram_api.domain import InstagramConnectionId, InstagramMessageId
from instagram_api.infrastructure.meta.http import MetaHttpMethod, MetaJsonExecutor

from .detail_policy import MetaInstagramMessageDetailAvailabilityPolicy
from .dto import MetaInstagramMessageDetailDto, MetaInstagramMessageSummaryDto
from .parser import MetaInstagramMessagingPayloadParser

MESSAGE_DETAIL_FIELDS = "id,created_time,from,to,message"


class MetaInstagramMessageDetailReader:
    """Reads message details only when Meta documents them as available."""

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
        position: int,
    ) -> MetaInstagramMessageDetailDto | None:
        """Return message details or None when detail lookup is ineligible."""

        if not self._availability_policy.can_read(summary, position):
            return None

        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path=str(InstagramMessageId(summary.id)),
            params={"fields": MESSAGE_DETAIL_FIELDS},
        )
        return self._parser.parse_message_detail(payload)
