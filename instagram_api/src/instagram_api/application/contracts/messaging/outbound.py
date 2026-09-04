"""Outbound Instagram messaging provider contracts."""

from typing import Protocol

from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMessageSendRequest,
    InstagramMessageSendResult,
    InstagramUserId,
)


class InstagramMessageRecipientEligibilityChecker(Protocol):
    """Checks whether a recipient has an existing eligible conversation."""

    async def is_eligible(
        self,
        connection_id: InstagramConnectionId,
        recipient_id: InstagramUserId,
    ) -> bool:
        """Return whether the recipient can be messaged through this connection."""
        ...


class InstagramOutboundMessageProvider(Protocol):
    """Sends a normalized message through one explicit connection."""

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        """Send a message through the selected provider connection."""
        ...
