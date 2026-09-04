"""Parser for Meta comment webhook values."""

from collections.abc import Mapping

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .comment_dto import MetaInstagramCommentWebhookDto
from .comment_fields import MetaInstagramCommentWebhookFieldParser


class MetaInstagramCommentWebhookPayloadParser:
    """Validates comment webhook values into typed provider DTOs."""

    def __init__(self, fields: MetaInstagramCommentWebhookFieldParser) -> None:
        self._fields = fields

    def parse(
        self,
        *,
        field: str,
        value: Mapping[str, object],
    ) -> MetaInstagramCommentWebhookDto:
        """Parse one comment or live-comment webhook value."""

        comment_id = self._fields.optional_string(value.get("id"))
        if comment_id is None:
            raise MetaInvalidResponseError(
                message="Meta comment webhook is missing a valid comment id.",
                status_code=200,
            )

        from_mapping = self._fields.mapping(value.get("from"))
        commenter_id: str | None = None
        commenter_username: str | None = None
        if from_mapping is not None:
            commenter_id = self._fields.optional_string(from_mapping.get("id"))
            commenter_username = self._fields.optional_string(
                from_mapping.get("username")
            )

        media_mapping = self._fields.mapping(value.get("media"))
        media_id: str | None = None
        media_product_type: str | None = None
        if media_mapping is not None:
            media_id = self._fields.optional_string(media_mapping.get("id"))
            media_product_type = self._fields.optional_string(
                media_mapping.get("media_product_type")
            )

        return MetaInstagramCommentWebhookDto(
            comment_id=comment_id,
            media_id=media_id,
            commenter_id=commenter_id,
            commenter_username=commenter_username,
            text=self._fields.optional_string(value.get("text")),
            parent_comment_id=self._fields.nested_id(value.get("parent_id")),
            media_product_type=media_product_type,
            is_live=field == "live_comments",
        )
