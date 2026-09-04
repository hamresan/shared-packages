"""Meta Instagram comment provider tests."""

import asyncio

from instagram_api.domain import (
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMediaId,
    InstagramUserId,
    PaginationCursor,
)
from instagram_api.infrastructure.meta.http import MetaHttpResponse
from tests.infrastructure.meta.comments.factories import build_comment_provider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def test_provider_lists_comments_with_pagination_and_normalized_fields() -> None:
    connection_id = InstagramConnectionId("connection")
    media_id = InstagramMediaId("media")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"data":[{"id":"comment","text":"hello","timestamp":'
                    b'"2026-09-04T10:00:00+0000","from":{"id":"author"},'
                    b'"media":{"id":"media"}}],"paging":{"cursors":{"after":"next"}}}'
                ),
            )
        ]
    )
    provider = build_comment_provider(transport, connection_id)

    page = asyncio.run(
        provider.list_comments(
            connection_id,
            media_id,
            PaginationCursor("cursor"),
        )
    )

    comment = page.items[0]
    assert comment.id == InstagramCommentId("comment")
    assert comment.media_id == media_id
    assert comment.author_id == InstagramUserId("author")
    assert comment.text == "hello"
    assert comment.parent_comment_id is None
    assert page.next_cursor == PaginationCursor("next")
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/media/comments")
    assert request.params["after"] == "cursor"


def test_provider_lists_replies_and_preserves_parent_relationship() -> None:
    connection_id = InstagramConnectionId("connection")
    comment_id = InstagramCommentId("parent")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"data":[{"id":"reply","text":"owner reply","timestamp":'
                    b'"2026-09-04T10:01:00+0000","from":{"id":"owner"},'
                    b'"media":{"id":"media"}}]}'
                ),
            )
        ]
    )
    provider = build_comment_provider(transport, connection_id)

    page = asyncio.run(provider.list_replies(connection_id, comment_id))

    reply = page.items[0]
    assert reply.id == InstagramCommentId("reply")
    assert reply.media_id == InstagramMediaId("media")
    assert reply.author_id == InstagramUserId("owner")
    assert reply.parent_comment_id == comment_id
    assert transport.requests[0].url.endswith("/v24.0/parent/replies")
