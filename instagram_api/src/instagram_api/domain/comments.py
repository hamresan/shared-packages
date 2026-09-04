"""Normalized Instagram comment models."""

from dataclasses import dataclass
from datetime import datetime

from .identifiers import (
    InstagramCommentId,
    InstagramMediaId,
    InstagramUserId,
)


@dataclass(frozen=True, slots=True)
class InstagramComment:
    """A provider-neutral Instagram comment or reply."""

    id: InstagramCommentId
    media_id: InstagramMediaId
    author_id: InstagramUserId
    text: str
    created_at: datetime
    parent_comment_id: InstagramCommentId | None = None


@dataclass(frozen=True, slots=True)
class InstagramCommentReplyResult:
    """Normalized result returned after a comment reply is accepted."""

    comment_id: InstagramCommentId
