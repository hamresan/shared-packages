"""Instagram outbound messaging contracts."""

from typing import Protocol

from instagram_api.domain.identifiers import InstagramConnectionId
from instagram_api.domain.messaging import (
    InstagramMessageSendRequest,
    InstagramMessageSendResult,
)


class InstagramMessageSender(Protocol):
    """Sends a message through one explicit Instagram connection."""

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        """Send a supported message through the requested connection."""
        ...
