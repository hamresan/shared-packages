"""Host-owned automation stub dispatching replies through the resolved connection."""

from instagram_api.application.contracts import (
    InstagramMessageSender,
    InstagramPublicCommentReplier,
    InstagramWebhookEventDispatcher,
)
from instagram_api.domain import (
    InstagramCommentCreated,
    InstagramConnectionId,
    InstagramMessageReceived,
    InstagramMessageSendRequest,
    InstagramWebhookEvent,
)


class HostAutomationDispatcher(InstagramWebhookEventDispatcher):
    """Demonstrates connection-preserving automation decisions."""

    def __init__(
        self,
        message_sender: InstagramMessageSender,
        comment_replier: InstagramPublicCommentReplier,
    ) -> None:
        self._message_sender = message_sender
        self._comment_replier = comment_replier

    async def dispatch(
        self,
        connection_id: InstagramConnectionId,
        event: InstagramWebhookEvent,
    ) -> None:
        payload = event.payload

        if isinstance(payload, InstagramMessageReceived):
            await self._message_sender.send_message(
                connection_id,
                InstagramMessageSendRequest(
                    recipient_id=payload.sender_id,
                    text="Thanks for your message.",
                    correlation_id=event.event_id,
                ),
            )
            return

        if isinstance(payload, InstagramCommentCreated):
            await self._comment_replier.reply_publicly(
                connection_id,
                payload.comment_id,
                "Thanks for your comment.",
            )
