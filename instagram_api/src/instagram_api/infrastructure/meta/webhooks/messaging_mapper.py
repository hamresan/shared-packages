"""Coordinates Meta messaging webhook variant mapping."""

from collections.abc import Mapping

from instagram_api.domain import (
    InstagramMessagingWebhookPayload,
    InstagramUserId,
)

from .message_mapper import MetaInstagramMessageWebhookMapper
from .messaging_fields import MetaInstagramMessagingWebhookFieldParser
from .metadata_mapper import MetaInstagramMessagingMetadataMapper


class MetaInstagramMessagingWebhookMapper:
    """Coordinates supported Meta messaging webhook variant mappers."""

    def __init__(
        self,
        fields: MetaInstagramMessagingWebhookFieldParser,
        message_mapper: MetaInstagramMessageWebhookMapper,
        metadata_mapper: MetaInstagramMessagingMetadataMapper,
    ) -> None:
        self._fields = fields
        self._message_mapper = message_mapper
        self._metadata_mapper = metadata_mapper

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

        raw_message = item.get("message")
        if raw_message is not None:
            message = self._fields.mapping(raw_message, "message")
            return self._message_mapper.to_domain(
                sender_id=sender_id,
                recipient_id=recipient_id,
                occurred_at=occurred_at,
                message=message,
            )

        return self._metadata_mapper.to_domain(
            sender_id=sender_id,
            recipient_id=recipient_id,
            occurred_at=occurred_at,
            item=item,
        )
