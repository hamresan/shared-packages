"""Host boundary for normalized Instagram messaging webhook events."""

from typing import Protocol

from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMessagingWebhookPayload,
)


class InstagramMessagingWebhookHandler(Protocol):
    """Handles normalized messaging webhook payloads in host-owned logic."""

    async def handle(
        self,
        connection_id: InstagramConnectionId,
        payload: InstagramMessagingWebhookPayload,
    ) -> None:
        """Handle a normalized messaging event for the resolved connection."""
        ...
