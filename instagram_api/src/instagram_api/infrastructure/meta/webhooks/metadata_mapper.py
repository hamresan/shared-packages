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

        raw_postback = item.get("postback")
        if raw_postback is not None:
            postback = self._fields.mapping(raw_postback, "postback")
            return InstagramMessagePostbackReceived(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._fields.required_message_id(postback)),
                title=self._fields.optional_string(postback.get("title")),
                payload=self._fields.optional_string(postback.get("payload")),
            )

        raw_read = item.get("read")
        if raw_read is not None:
            read = self._fields.mapping(raw_read, "read")
            return InstagramMessageRead(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._fields.required_message_id(read)),
            )

        raw_reaction = item.get("reaction")
        if raw_reaction is not None:
            reaction = self._fields.mapping(raw_reaction, "reaction")
            action = reaction.get("action")
            if not isinstance(action, str) or action not in {"react", "unreact"}:
                raise MetaInvalidResponseError(
                    message="Meta messaging reaction action is invalid.",
                    status_code=200,
                )
            return InstagramMessageReaction(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._fields.required_message_id(reaction)),
                action=InstagramMessageReactionAction(action),
                reaction=self._fields.optional_string(reaction.get("reaction")),
                emoji=self._fields.optional_string(reaction.get("emoji")),
            )

        raw_edit = item.get("message_edit")
        if raw_edit is not None:
            edited = self._fields.mapping(raw_edit, "message edit")
            return InstagramMessageEdited(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._fields.required_message_id(edited)),
                text=self._fields.optional_string(edited.get("text")),
                edit_count=self._fields.optional_int(edited.get("num_edit")),
            )

        raw_referral = item.get("referral")
        if raw_referral is not None:
            referral = self._fields.mapping(raw_referral, "referral")
            return InstagramMessagingReferralReceived(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                referral_ref=self._fields.optional_string(referral.get("ref")),
                source=self._fields.optional_string(referral.get("source")),
                referral_type=self._fields.optional_string(referral.get("type")),
            )

        return None
