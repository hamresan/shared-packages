"""Maps Meta message webhook payloads to normalized inbound messages."""

from collections.abc import Mapping
from datetime import datetime

from instagram_api.domain import (
    InstagramInboundMessageAttachment,
    InstagramMessageId,
    InstagramMessageReceived,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .messaging_fields import MetaInstagramMessagingWebhookFieldParser


class MetaInstagramMessageWebhookMapper:
    """Maps the Meta message variant to a normalized inbound message."""

    def __init__(self, fields: MetaInstagramMessagingWebhookFieldParser) -> None:
        self._fields = fields

    def to_domain(
        self,
        *,
        sender_id: InstagramUserId,
        recipient_id: InstagramUserId,
        occurred_at: datetime,
        message: Mapping[str, object],
    ) -> InstagramMessageReceived:
        """Map one Meta message object."""

        mid = message.get("mid")
        if not isinstance(mid, str) or not mid:
            raise MetaInvalidResponseError(
                message="Meta messaging webhook is missing a valid message id.",
                status_code=200,
            )

        attachments: list[InstagramInboundMessageAttachment] = []
        for raw_attachment in self._fields.sequence(message.get("attachments")):
            attachment = self._fields.mapping(raw_attachment, "attachment")
            payload = attachment.get("payload")
            url: str | None = None
            if isinstance(payload, Mapping):
                payload_mapping = self._fields.mapping(
                    payload,
                    "attachment payload",
                )
                url = self._fields.optional_string(payload_mapping.get("url"))
            attachments.append(
                InstagramInboundMessageAttachment(
                    attachment_type=self._fields.optional_string(attachment.get("type")),
                    url=url,
                )
            )

        story_id: str | None = None
        story_url: str | None = None
        reply_to = message.get("reply_to")
        if isinstance(reply_to, Mapping):
            reply_mapping = self._fields.mapping(reply_to, "reply_to")
            story = reply_mapping.get("story")
            if isinstance(story, Mapping):
                story_mapping = self._fields.mapping(story, "story")
                story_id = self._fields.optional_string(story_mapping.get("id"))
                story_url = self._fields.optional_string(story_mapping.get("url"))

        return InstagramMessageReceived(
            sender_id=sender_id,
            recipient_id=recipient_id,
            occurred_at=occurred_at,
            message_id=InstagramMessageId(mid),
            text=self._fields.optional_string(message.get("text")),
            attachments=tuple(attachments),
            is_echo=self._fields.optional_bool(message.get("is_echo")),
            is_self=self._fields.optional_bool(message.get("is_self")),
            is_deleted=self._fields.optional_bool(message.get("is_deleted")),
            is_unsupported=self._fields.optional_bool(message.get("is_unsupported")),
            reply_to_story_id=story_id,
            reply_to_story_url=story_url,
        )
