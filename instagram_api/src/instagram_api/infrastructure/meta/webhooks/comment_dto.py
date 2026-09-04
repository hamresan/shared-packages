"""Provider DTO for Meta comment webhook values."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramCommentWebhookDto:
    """Typed Meta comment webhook value."""

    comment_id: str
    media_id: str | None
    commenter_id: str | None
    commenter_username: str | None
    text: str | None
    parent_comment_id: str | None
    media_product_type: str | None
    is_live: bool
