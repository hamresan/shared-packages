"""Parsers for Meta Instagram conversation and message payloads."""

from collections.abc import Mapping, Sequence
from typing import cast

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import (
    MetaInstagramConversationDto,
    MetaInstagramMessageDetailDto,
    MetaInstagramMessageSummaryDto,
)


class MetaInstagramMessagingPayloadParser:
    """Validates Meta messaging payloads into typed DTOs."""

    def parse_conversations(
        self,
        payload: Mapping[str, object],
    ) -> tuple[MetaInstagramConversationDto, ...]:
        data = self._data_sequence(payload.get("data"), "conversation")
        items: list[MetaInstagramConversationDto] = []
        for item in data:
            mapping = self._mapping(item, "conversation")
            conversation_id = self._required_string(mapping.get("id"), "conversation id")
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
        messages = self._mapping(payload.get("messages"), "messages")
        data = self._data_sequence(messages.get("data"), "message")
        items: list[MetaInstagramMessageSummaryDto] = []
        for item in data:
            mapping = self._mapping(item, "message")
            message_id = self._required_string(mapping.get("id"), "message id")
            created = self._required_string(mapping.get("created_time"), "created_time")
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
        message_id = self._required_string(payload.get("id"), "message id")
        created = self._required_string(payload.get("created_time"), "created_time")
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

    @staticmethod
    def _mapping(value: object, label: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise MetaInvalidResponseError(
                message=f"Meta {label} payload is invalid.",
                status_code=200,
            )
        return cast(Mapping[str, object], value)

    @staticmethod
    def _data_sequence(value: object, label: str) -> Sequence[object]:
        if not isinstance(value, Sequence) or isinstance(value, str | bytes):
            raise MetaInvalidResponseError(
                message=f"Meta {label} collection is invalid.",
                status_code=200,
            )
        return cast(Sequence[object], value)

    @staticmethod
    def _required_string(value: object, label: str) -> str:
        if not isinstance(value, str) or not value:
            raise MetaInvalidResponseError(
                message=f"Meta payload is missing a valid {label}.",
                status_code=200,
            )
        return value
