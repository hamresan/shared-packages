"""Normalized Instagram comment webhook payloads."""

from dataclasses import dataclass

from .identifiers import InstagramCommentId, InstagramMediaId, InstagramUserId
from .webhook_payloads import InstagramWebhookPayload


@dataclass(frozen=True, slots=True)
class InstagramCommentWebhookPayload(InstagramWebhookPayload):
    """Shared normalized comment webhook fields."""

    comment_id: InstagramCommentId
    media_id: InstagramMediaId | None = None
    commenter_id: InstagramUserId | None = None
    commenter_username: str | None = None
    text: str | None = None
    parent_comment_id: InstagramCommentId | None = None
    media_product_type: str | None = None
    is_live: bool = False


@dataclass(frozen=True, slots=True)
class InstagramCommentCreated(InstagramCommentWebhookPayload):
    """Normalized direct comment webhook notification."""


@dataclass(frozen=True, slots=True)
class InstagramCommentChanged(InstagramCommentWebhookPayload):
    """Normalized comment change notification."""
