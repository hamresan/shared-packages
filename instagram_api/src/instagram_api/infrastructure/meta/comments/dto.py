"""Provider DTOs for Meta Instagram comments."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramCommentDto:
    """Typed Meta comment payload."""

    id: str
    media_id: str | None
    author_id: str
    text: str
    timestamp: str
    parent_comment_id: str | None
