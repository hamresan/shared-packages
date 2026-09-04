"""Parser for Meta Instagram comment payloads."""

from collections.abc import Mapping, Sequence
from typing import cast

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import MetaInstagramCommentDto
from .fields import MetaInstagramCommentFieldParser


class MetaInstagramCommentPayloadParser:
    """Validates Meta comment payloads and produces typed DTOs."""

    def __init__(self, field_parser: MetaInstagramCommentFieldParser) -> None:
        self._field_parser = field_parser

    def parse_comment(
        self,
        payload: Mapping[str, object],
        fallback_media_id: str | None = None,
        fallback_parent_id: str | None = None,
    ) -> MetaInstagramCommentDto:
        """Parse one comment or reply."""

        comment_id = payload.get("id")
        text = payload.get("text")
        timestamp = payload.get("timestamp")
        media_id = self._field_parser.media_id(payload.get("media")) or fallback_media_id
        author_id = self._field_parser.author_id(payload.get("from"))
        parent_id = self._field_parser.parent_id(payload.get("parent_id")) or fallback_parent_id

        required_values = (comment_id, author_id, text, timestamp)
        if not all(isinstance(value, str) and value for value in required_values):
            raise MetaInvalidResponseError(
                message="Meta comment response is missing required fields.",
                status_code=200,
            )

        return MetaInstagramCommentDto(
            id=cast(str, comment_id),
            media_id=media_id,
            author_id=cast(str, author_id),
            text=cast(str, text),
            timestamp=cast(str, timestamp),
            parent_comment_id=parent_id,
        )

    def parse_collection(
        self,
        payload: Mapping[str, object],
        fallback_media_id: str | None = None,
        fallback_parent_id: str | None = None,
    ) -> tuple[MetaInstagramCommentDto, ...]:
        """Parse a Meta comment collection."""

        data = payload.get("data")
        if not isinstance(data, Sequence) or isinstance(data, str | bytes):
            raise MetaInvalidResponseError(
                message="Meta comment response is missing a valid data collection.",
                status_code=200,
            )

        raw_items = cast(Sequence[object], data)
        items: list[MetaInstagramCommentDto] = []
        for raw_item in raw_items:
            if not isinstance(raw_item, Mapping):
                raise MetaInvalidResponseError(
                    message="Meta comment collection contains an invalid item.",
                    status_code=200,
                )
            items.append(
                self.parse_comment(
                    cast(Mapping[str, object], raw_item),
                    fallback_media_id,
                    fallback_parent_id,
                )
            )
        return tuple(items)
