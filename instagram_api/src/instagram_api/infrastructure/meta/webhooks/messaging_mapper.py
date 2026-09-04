"""Maps Meta messaging webhook items to package-owned payloads."""

from collections.abc import Mapping

from instagram_api.domain import (
    InstagramInboundMessageAttachment,
    InstagramMessageEdited,
    InstagramMessageId,
    InstagramMessagePostbackReceived,
    InstagramMessageReaction,
    InstagramMessageReactionAction,
    InstagramMessageRead,
    InstagramMessageReceived,
    InstagramMessagingReferralReceived,
    InstagramMessagingWebhookPayload,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .messaging_fields import MetaInstagramMessagingWebhookFieldParser


class MetaInstagramMessagingWebhookMapper:
    """Normalizes supported Meta messaging webhook variants."""

    def __init__(self, fields: MetaInstagramMessagingWebhookFieldParser) -> None:
        self._fields = fields

    def to_domain(
        self,
        item: Mapping[str, object],
    ) -> InstagramMessagingWebhookPayload | None:
        """Map one supported messaging item or return None for an unknown variant."""

        sender_id = InstagramUserId(
            self._fields.required_id(item.get("sender"), "sender")
        )
        recipient_id = InstagramUserId(
            self._fields.required_id(item.get("recipient"), "recipient")
        )
        occurred_at = self._fields.timestamp(item.get("timestamp"))

        message = item.get("message")
        if isinstance(message, Mapping):
            return self._message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message=message,
            )

        postback = item.get("postback")
        if isinstance(postback, Mapping):
            message_id = self._required_mid(postback)
            return InstagramMessagePostbackReceived(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(message_id),
                title=self._fields.optional_string(postback.get("title")),
                payload=self._fields.optional_string(postback.get("payload")),
            )

        read = item.get("read")
        if isinstance(read, Mapping):
            return InstagramMessageRead(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message_id=InstagramMessageId(self._required_mid(read)),
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
                message_id=InstagramMessageId(self._required_mid(reaction)),
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
                message_id=InstagramMessageId(self._required_mid(edited)),
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

    def _message(
        self,
        *,
        sender_id: InstagramUserId,
        recipient_id: InstagramUserId,
        occurred_at: object,
        message: Mapping[str, object],
    ) -> InstagramMessageReceived:
        if not hasattr(occurred_at, "tzinfo"):
            raise MetaInvalidResponseError(
                message="Meta messaging webhook timestamp is invalid.",
                status_code=200,
            )

        attachments: list[InstagramInboundMessageAttachment] = []
        for raw_attachment in self._fields.sequence(message.get("attachments")):
            attachment = self._fields.mapping(raw_attachment, "attachment")
            payload = attachment.get("payload")
            url: str | None = None
            if isinstance(payload, Mapping):
                url = self._fields.optional_string(payload.get("url"))
            attachments.append(
                InstagramInboundMessageAttachment(
                    attachment_type=self._fields.optional_string(
                        attachment.get("type")
                    ),
                    url=url,
                )
            )

        story_id: str | None = None
        story_url: str | None = None
        reply_to = message.get("reply_to")
        if isinstance(reply_to, Mapping):
            story = reply_to.get("story")
            if isinstance(story, Mapping):
                story_id = self._fields.optional_string(story.get("id"))
                story_url = self._fields.optional_string(story.get("url"))

        return InstagramMessageReceived(
            sender_id=sender_id,
            recipient_id=recipient_id,
            occurred_at=occurred_at,
            message_id=InstagramMessageId(self._required_mid(message)),
            text=self._fields.optional_string(message.get("text")),
            attachments=tuple(attachments),
            is_echo=self._fields.optional_bool(message.get("is_echo")),
            is_self=self._fields.optional_bool(message.get("is_self")),
            is_deleted=self._fields.optional_bool(message.get("is_deleted")),
            is_unsupported=self._fields.optional_bool(message.get("is_unsupported")),
            reply_to_story_id=story_id,
            reply_to_story_url=story_url,
        )

    def _required_mid(self, payload: Mapping[str, object]) -> str:
        mid = payload.get("mid")
        if not isinstance(mid, str) or not mid:
            raise MetaInvalidResponseError(
                message="Meta messaging webhook is missing a valid message id.",
                status_code=200,
            )
        return mid
