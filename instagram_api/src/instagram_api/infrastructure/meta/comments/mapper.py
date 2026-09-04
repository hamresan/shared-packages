"""Mapper for Meta Instagram comment DTOs."""

from instagram_api.domain import (
    InstagramComment,
    InstagramCommentId,
    InstagramMediaId,
    InstagramUserId,
)

from .dto import MetaInstagramCommentDto
from .timestamp_parser import MetaInstagramCommentTimestampParser


class MetaInstagramCommentMapper:
    """Maps typed Meta comment DTOs to normalized domain comments."""

    def __init__(self, timestamp_parser: MetaInstagramCommentTimestampParser) -> None:
        self._timestamp_parser = timestamp_parser

    def to_domain(self, dto: MetaInstagramCommentDto) -> InstagramComment:
        """Map one provider DTO to a normalized comment."""

        parent_id = (
            InstagramCommentId(dto.parent_comment_id) if dto.parent_comment_id is not None else None
        )
        return InstagramComment(
            id=InstagramCommentId(dto.id),
            media_id=InstagramMediaId(dto.media_id) if dto.media_id is not None else None,
            author_id=InstagramUserId(dto.author_id),
            text=dto.text,
            created_at=self._timestamp_parser.parse(dto.timestamp),
            parent_comment_id=parent_id,
        )
