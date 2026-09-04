"""Maps Meta comment webhook values to package-owned payloads."""

from collections.abc import Mapping

from instagram_api.domain import (
    InstagramCommentChanged,
    InstagramCommentCreated,
    InstagramCommentId,
    InstagramCommentWebhookPayload,
    InstagramMediaId,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .comment_fields import MetaInstagramCommentWebhookFieldParser


class MetaInstagramCommentWebhookMapper:
    """Normalizes supported Meta comment and live-comment webhook values."""

    def __init__(self, fields: MetaInstagramCommentWebhookFieldParser) -> None:
        self._fields = fields

    def created(
        self,
        *,
        field: str,
        value: Mapping[str, object],
    ) -> InstagramCommentCreated:
        """Map a direct Meta comment webhook notification."""

        data = self._common(field=field, value=value)
        return InstagramCommentCreated(**data)

    def changed(
        self,
        *,
        field: str,
        value: Mapping[str, object],
    ) -> InstagramCommentChanged:
        """Map a comment item delivered through a changes collection."""

        data = self._common(field=field, value=value)
        return InstagramCommentChanged(**data)

    def _common(
        self,
        *,
        field: str,
        value: Mapping[str, object],
    ) -> dict[str, object]:
        comment_id = self._fields.optional_string(value.get("id"))
        if comment_id is None:
            raise MetaInvalidResponseError(
                message="Meta comment webhook is missing a valid comment id.",
                status_code=200,
            )

        from_mapping = self._fields.mapping(value.get("from"))
        commenter_id: InstagramUserId | None = None
        commenter_username: str | None = None
        if from_mapping is not None:
            raw_commenter_id = self._fields.optional_string(from_mapping.get("id"))
            if raw_commenter_id is not None:
                commenter_id = InstagramUserId(raw_commenter_id)
            commenter_username = self._fields.optional_string(
                from_mapping.get("username")
            )

        media_mapping = self._fields.mapping(value.get("media"))
        media_id: InstagramMediaId | None = None
        media_product_type: str | None = None
        if media_mapping is not None:
            raw_media_id = self._fields.optional_string(media_mapping.get("id"))
            if raw_media_id is not None:
                media_id = InstagramMediaId(raw_media_id)
            media_product_type = self._fields.optional_string(
                media_mapping.get("media_product_type")
            )

        parent_id = self._fields.nested_id(value.get("parent_id"))

        return {
            "comment_id": InstagramCommentId(comment_id),
            "media_id": media_id,
            "commenter_id": commenter_id,
            "commenter_username": commenter_username,
            "text": self._fields.optional_string(value.get("text")),
            "parent_comment_id": (
                InstagramCommentId(parent_id) if parent_id is not None else None
            ),
            "media_product_type": media_product_type,
            "is_live": field == "live_comments",
        }
