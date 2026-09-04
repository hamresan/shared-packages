"""Meta Instagram comment mapper tests."""

import pytest

from instagram_api.domain import InstagramCommentId, InstagramMediaId, InstagramUserId
from instagram_api.infrastructure.meta.comments import (
    MetaInstagramCommentDto,
    MetaInstagramCommentMapper,
    MetaInstagramCommentTimestampParser,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


def test_mapper_maps_reply_relationship_and_timestamp() -> None:
    mapper = MetaInstagramCommentMapper(MetaInstagramCommentTimestampParser())

    comment = mapper.to_domain(
        MetaInstagramCommentDto(
            id="reply",
            media_id="media",
            author_id="author",
            text="hello",
            timestamp="2026-09-04T10:00:00+0000",
            parent_comment_id="parent",
        )
    )

    assert comment.id == InstagramCommentId("reply")
    assert comment.media_id == InstagramMediaId("media")
    assert comment.author_id == InstagramUserId("author")
    assert comment.parent_comment_id == InstagramCommentId("parent")


def test_mapper_rejects_invalid_timestamp() -> None:
    mapper = MetaInstagramCommentMapper(MetaInstagramCommentTimestampParser())

    with pytest.raises(MetaInvalidResponseError):
        mapper.to_domain(
            MetaInstagramCommentDto(
                id="comment",
                media_id="media",
                author_id="author",
                text="hello",
                timestamp="invalid",
                parent_comment_id=None,
            )
        )
