"""Instagram comment service tests."""

import asyncio
from datetime import UTC, datetime

from instagram_api.application.comments import (
    InstagramCommentAccessPolicy,
    InstagramCommentService,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramComment,
    InstagramCommentId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramMediaId,
    InstagramUserId,
    Page,
    PaginationCursor,
)
from tests.fakes import FakeInstagramCommentProvider, FakeInstagramConnectionReader


def test_comment_service_keeps_connections_isolated_and_forwards_cursors() -> None:
    first_id = InstagramConnectionId("connection-a")
    second_id = InstagramConnectionId("connection-b")
    media_id = InstagramMediaId("media")
    comment_id = InstagramCommentId("comment")
    permissions = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_comments",
        }
    )
    now = datetime.now(UTC)
    comment = InstagramComment(
        comment_id,
        media_id,
        InstagramUserId("author"),
        "hello",
        now,
    )
    provider = FakeInstagramCommentProvider(
        {
            (first_id, media_id): Page((comment,)),
            (second_id, media_id): Page(()),
        },
        {
            (first_id, comment_id): Page(()),
            (second_id, comment_id): Page((comment,)),
        },
    )
    service = InstagramCommentService(
        FakeInstagramConnectionReader(
            {
                first_id: InstagramConnection(
                    first_id,
                    InstagramAccountId("account-a"),
                    permissions,
                    True,
                ),
                second_id: InstagramConnection(
                    second_id,
                    InstagramAccountId("account-b"),
                    permissions,
                    True,
                ),
            }
        ),
        provider,
        InstagramCommentAccessPolicy(),
    )

    first_page = asyncio.run(
        service.list_comments(first_id, media_id, PaginationCursor("comments-cursor"))
    )
    second_page = asyncio.run(
        service.list_replies(second_id, comment_id, PaginationCursor("replies-cursor"))
    )

    assert first_page.items == (comment,)
    assert second_page.items == (comment,)
    assert provider.comment_calls == [(first_id, media_id, PaginationCursor("comments-cursor"))]
    assert provider.reply_calls == [(second_id, comment_id, PaginationCursor("replies-cursor"))]
