"""Meta public comment reply provider tests."""

import asyncio

import pytest

from instagram_api.application.comments import InstagramPublicReplyRejectedError
from instagram_api.domain import (
    InstagramCommentId,
    InstagramConnectionId,
)
from instagram_api.infrastructure.meta.http import MetaHttpResponse, MetaTransientError
from tests.infrastructure.meta.comments.reply_factories import build_public_reply_provider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def test_public_reply_provider_posts_to_comment_replies_edge() -> None:
    connection_id = InstagramConnectionId("connection")
    comment_id = InstagramCommentId("comment")
    transport = SequenceMetaHttpTransport([MetaHttpResponse(200, {}, b'{"id":"reply"}')])
    provider = build_public_reply_provider(transport, connection_id)

    result = asyncio.run(provider.reply(connection_id, comment_id, "thanks"))

    assert result.comment_id == InstagramCommentId("reply")
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/comment/replies")
    assert request.params == {"message": "thanks"}
    assert request.headers["Authorization"] == "Bearer token"


def test_public_reply_provider_normalizes_rejection_and_never_retries_post() -> None:
    connection_id = InstagramConnectionId("connection")
    comment_id = InstagramCommentId("comment")

    rejected_transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                400,
                {},
                b'{"error":{"message":"reply rejected","code":10}}',
            )
        ]
    )
    rejected_provider = build_public_reply_provider(rejected_transport, connection_id)

    with pytest.raises(InstagramPublicReplyRejectedError):
        asyncio.run(rejected_provider.reply(connection_id, comment_id, "thanks"))

    transient_transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                500,
                {},
                b'{"error":{"message":"temporary","code":2}}',
            ),
            MetaHttpResponse(200, {}, b'{"id":"duplicate-risk"}'),
        ]
    )
    transient_provider = build_public_reply_provider(transient_transport, connection_id)

    with pytest.raises(MetaTransientError):
        asyncio.run(transient_provider.reply(connection_id, comment_id, "thanks"))

    assert len(transient_transport.requests) == 1
