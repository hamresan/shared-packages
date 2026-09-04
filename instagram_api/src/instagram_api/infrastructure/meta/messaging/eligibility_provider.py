"""Meta recipient eligibility checker for outbound Instagram messages."""

from instagram_api.application.contracts.messaging import (
    InstagramMessageRecipientEligibilityChecker,
)
from instagram_api.domain import InstagramConnectionId, InstagramUserId
from instagram_api.infrastructure.meta.http import MetaHttpMethod, MetaJsonExecutor

from .parser import MetaInstagramMessagingPayloadParser


class MetaInstagramMessageRecipientEligibilityChecker(InstagramMessageRecipientEligibilityChecker):
    """Checks for an existing conversation with the intended recipient."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramMessagingPayloadParser,
    ) -> None:
        self._executor = executor
        self._parser = parser

    async def is_eligible(
        self,
        connection_id: InstagramConnectionId,
        recipient_id: InstagramUserId,
    ) -> bool:
        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path="me/conversations",
            params={"user_id": str(recipient_id)},
        )
        return bool(self._parser.parse_conversations(payload))
