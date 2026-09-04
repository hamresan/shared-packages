"""Default webhook failure handling policies."""

from instagram_api.application.contracts.webhooks import (
    InstagramWebhookFailureDecision,
    InstagramWebhookFailureHandler,
)
from instagram_api.domain import InstagramConnectionId, InstagramWebhookEvent


class RetryInstagramWebhookFailureHandler(InstagramWebhookFailureHandler):
    """Default policy that leaves failed events eligible for provider retry."""

    async def handle(
        self,
        event: InstagramWebhookEvent,
        connection_id: InstagramConnectionId | None,
        error: Exception,
    ) -> InstagramWebhookFailureDecision:
        del event, connection_id, error
        return InstagramWebhookFailureDecision.RETRY
