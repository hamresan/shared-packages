"""Maps Meta messaging metadata webhook variants."""

from collections.abc import Mapping
from datetime import datetime

from instagram_api.domain import (
    InstagramMessageEdited,
    InstagramMessageId,
    InstagramMessagePostbackReceived,
    InstagramMessageReaction,
    InstagramMessageReactionAction,
    InstagramMessageRead,
    InstagramMessagingReferralReceived,
    InstagramMessagingWebhookPayload,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .messaging_fields import MetaInstagramMessagingWebhookFieldParser


class MetaInstagramMessagingMetadataMapper:
    """Maps supported non-message messaging webhook variants."""

    def __init__(self, fields: MetaInstagramMessagingWebhookFieldParser) -> None:
        self._fields = fields

    def to_domain(
        self,
        *,
        sender_id: InstagramUserId,
        recipient_id: InstagramUserId,
        occurred_at: datetime,
        item: Mapping[str, object],
    ) -> InstagramMessagingWebhookPayload | None:
        """Map a supported metadata variant or return None."""

        postback = item.get("postback")
        if isinstance(postback, Mapping):
            return InstagramMessagePostbackReceived(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._message_id(postback)),
                title=self._fields.optional_string(postback.get("title")),
                payload=self._fields.optional_string(postback.get("payload")),
            )

        read = item.get("read")
        if isinstance(read, Mapping):
            return InstagramMessageRead(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._message_id(read)),
            )

        reaction = item.get("reaction")
        if isinstance(reaction, Mapping):
            action = reaction.get("action")
            if action not in {"react", "unreact"}:
                raise MetaInvalidResponseError(
                    message="Meta messaging reaction action is invalid.",
                    status_code=200,
                )
            return InstagramMessageReaction(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._message_id(reaction)),
                action=InstagramMessageReactionAction(action),
                reaction=self._fields.optional_string(reaction.get("reaction")),
                emoji=self._fields.optional_string(reaction.get("emoji")),
            )

        edited = item.get("message_edit")
        if isinstance(edited, Mapping):
            return InstagramMessageEdited(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._message_id(edited)),
                text=self._fields.optional_string(edited.get("text")),
                edit_count=self._fields.optional_int(edited.get("num_edit")),
            )

        referral = item.get("referral")
        if isinstance(referral, Mapping):
            return InstagramMessagingReferralReceived(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                referral_ref=self._fields.optional_string(referral.get("ref")),
                source=self._fields.optional_string(referral.get("source")),
                referral_type=self._fields.optional_string(referral.get("type")),
            )

        return None

    def _message_id(self, payload: Mapping[str, object]) -> str:
        mid = payload.get("mid")
        if not isinstance(mid, str) or not mid:
            raise MetaInvalidResponseError(
                message="Meta messaging webhook is missing a valid message id.",
                status_code=200,
            )
        return mid
