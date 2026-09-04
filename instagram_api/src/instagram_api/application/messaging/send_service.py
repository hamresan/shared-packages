"""Outbound Instagram messaging application service."""

from instagram_api.application.contracts.connection import InstagramConnectionReader
from instagram_api.application.contracts.messaging import (
    InstagramMessageRecipientEligibilityChecker,
    InstagramMessageSender,
    InstagramOutboundMessageProvider,
)
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMessageSendRequest,
    InstagramMessageSendResult,
)

from .send_errors import InstagramMessageRecipientIneligibleError
from .send_policy import InstagramMessagePayloadPolicy, InstagramMessageSendAccessPolicy


class InstagramMessageSendService(InstagramMessageSender):
    """Sends eligible messages through one explicit Instagram connection."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        eligibility_checker: InstagramMessageRecipientEligibilityChecker,
        provider: InstagramOutboundMessageProvider,
        access_policy: InstagramMessageSendAccessPolicy,
        payload_policy: InstagramMessagePayloadPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._eligibility_checker = eligibility_checker
        self._provider = provider
        self._access_policy = access_policy
        self._payload_policy = payload_policy

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        self._payload_policy.validate(request)

        is_eligible = await self._eligibility_checker.is_eligible(
            connection_id,
            request.recipient_id,
        )
        if not is_eligible:
            raise InstagramMessageRecipientIneligibleError(
                "Recipient has no eligible existing Instagram conversation."
            )

        result = await self._provider.send_message(connection_id, request)
        return InstagramMessageSendResult(
            message_id=result.message_id,
            recipient_id=result.recipient_id,
            correlation_id=request.correlation_id,
        )
