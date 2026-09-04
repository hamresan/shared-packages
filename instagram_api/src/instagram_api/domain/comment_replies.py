"""Normalized Instagram comment reply models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .identifiers import InstagramCommentId, InstagramMessageId, InstagramUserId


class InstagramPrivateReplySource(StrEnum):
    """Provider reply source categories with distinct timing rules."""

    STANDARD = "standard"
    LIVE = "live"


@dataclass(frozen=True, slots=True)
class InstagramPrivateCommentReplyRequest:
    """Private-reply request with explicit eligibility context."""

    comment_id: InstagramCommentId
    text: str
    comment_created_at: datetime
    source: InstagramPrivateReplySource
    live_is_active: bool | None = None


@dataclass(frozen=True, slots=True)
class InstagramPrivateCommentReplyResult:
    """Normalized result returned after a private comment reply is accepted."""

    message_id: InstagramMessageId
    recipient_id: InstagramUserId | None = None
