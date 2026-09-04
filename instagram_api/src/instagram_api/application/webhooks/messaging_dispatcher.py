"""Bridge from generic webhook dispatch to messaging-specific host handling."""

from instagram_api.application.contracts.webhooks import (
    InstagramMessagingWebhookHandler,
    InstagramWebhookEventDispatcher,
)
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMessagingWebhookPayload,
    InstagramWebhookEvent,
)


class InstagramMessagingWebhookDispatcher(InstagramWebhookEventDispatcher):
    """Dispatches only normalized messaging payloads to the host handler."""

    def __init__(self, handler: InstagramMessagingWebhookHandler) -> None:
        self._handler = handler

    async def dispatch(
        self,
        connection_id: InstagramConnectionId,
        event: InstagramWebhookEvent,
    ) -> None:
        payload = event.payload
        if isinstance(payload, InstagramMessagingWebhookPayload):
            await self._handler.handle(connection_id, payload)
