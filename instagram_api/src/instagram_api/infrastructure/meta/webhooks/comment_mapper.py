"""Maps typed Meta comment webhook DTOs to package-owned payloads."""

from instagram_api.domain import (
    InstagramCommentChanged,
    InstagramCommentCreated,
    InstagramCommentId,
    InstagramMediaId,
    InstagramUserId,
)

from .comment_dto import MetaInstagramCommentWebhookDto


class MetaInstagramCommentWebhookMapper:
    """Maps typed comment webhook DTOs to normalized domain payloads."""

    def created(
        self,
        dto: MetaInstagramCommentWebhookDto,
    ) -> InstagramCommentCreated:
        """Map a direct comment webhook DTO."""

        return InstagramCommentCreated(
            comment_id=InstagramCommentId(dto.comment_id),
            media_id=(
                InstagramMediaId(dto.media_id)
                if dto.media_id is not None
                else None
            ),
            commenter_id=(
                InstagramUserId(dto.commenter_id)
                if dto.commenter_id is not None
                else None
            ),
            commenter_username=dto.commenter_username,
            text=dto.text,
            parent_comment_id=(
                InstagramCommentId(dto.parent_comment_id)
                if dto.parent_comment_id is not None
                else None
            ),
            media_product_type=dto.media_product_type,
            is_live=dto.is_live,
        )

    def changed(
        self,
        dto: MetaInstagramCommentWebhookDto,
    ) -> InstagramCommentChanged:
        """Map a comment-change webhook DTO."""

        return InstagramCommentChanged(
            comment_id=InstagramCommentId(dto.comment_id),
            media_id=(
                InstagramMediaId(dto.media_id)
                if dto.media_id is not None
                else None
            ),
            commenter_id=(
                InstagramUserId(dto.commenter_id)
                if dto.commenter_id is not None
                else None
            ),
            commenter_username=dto.commenter_username,
            text=dto.text,
            parent_comment_id=(
                InstagramCommentId(dto.parent_comment_id)
                if dto.parent_comment_id is not None
                else None
            ),
            media_product_type=dto.media_product_type,
            is_live=dto.is_live,
        )
