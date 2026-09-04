"""Parsers for Meta Instagram conversation and message payloads."""

from collections.abc import Mapping
from typing import cast

from .dto import (
    MetaInstagramConversationDto,
    MetaInstagramMessageDetailDto,
    MetaInstagramMessageSummaryDto,
)
from .fields import MetaInstagramMessagingFieldParser


class MetaInstagramMessagingPayloadParser:
    """Validates Meta messaging payloads into typed DTOs."""

    def __init__(self, field_parser: MetaInstagramMessagingFieldParser) -> None:
        self._field_parser = field_parser

    def parse_conversations(
        self,
        payload: Mapping[str, object],
    ) -> tuple[MetaInstagramConversationDto, ...]:
        data = self._field_parser.sequence(payload.get("data"), "conversation")
        items: list[MetaInstagramConversationDto] = []
        for item in data:
            mapping = self._field_parser.mapping(item, "conversation")
            conversation_id = self._field_parser.required_string(
                mapping.get("id"),
                "conversation id",
            )
            updated = mapping.get("updated_time")
            items.append(
                MetaInstagramConversationDto(
                    id=conversation_id,
                    updated_time=updated if isinstance(updated, str) else None,
                )
            )
        return tuple(items)

    def parse_message_summaries(
        self,
        payload: Mapping[str, object],
    ) -> tuple[MetaInstagramMessageSummaryDto, ...]:
        messages = self._field_parser.mapping(payload.get("messages"), "messages")
        data = self._field_parser.sequence(messages.get("data"), "message")
        items: list[MetaInstagramMessageSummaryDto] = []
        for item in data:
            mapping = self._field_parser.mapping(item, "message")
            message_id = self._field_parser.required_string(mapping.get("id"), "message id")
            created = self._field_parser.required_string(
                mapping.get("created_time"),
                "created_time",
            )
            unsupported = mapping.get("is_unsupported")
            items.append(
                MetaInstagramMessageSummaryDto(
                    id=message_id,
                    created_time=created,
                    is_unsupported=unsupported if isinstance(unsupported, bool) else False,
                )
            )
        return tuple(items)

    def parse_message_detail(
        self,
        payload: Mapping[str, object],
    ) -> MetaInstagramMessageDetailDto:
        message_id = self._field_parser.required_string(payload.get("id"), "message id")
        created = self._field_parser.required_string(
            payload.get("created_time"),
            "created_time",
        )
        sender = payload.get("from")
        sender_id: str | None = None
        if isinstance(sender, Mapping):
            sender_mapping = cast(Mapping[str, object], sender)
            raw_sender_id = sender_mapping.get("id")
            sender_id = raw_sender_id if isinstance(raw_sender_id, str) else None
        raw_message = payload.get("message")
        return MetaInstagramMessageDetailDto(
            id=message_id,
            created_time=created,
            sender_id=sender_id,
            message=raw_message if isinstance(raw_message, str) else None,
        )

    def messages_container(
        self,
        payload: Mapping[str, object],
    ) -> Mapping[str, object]:
        """Return the nested messages object for pagination mapping."""

        return self._field_parser.mapping(payload.get("messages"), "messages")
