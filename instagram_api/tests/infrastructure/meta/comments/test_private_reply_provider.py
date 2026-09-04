"""Meta private comment reply provider tests."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.application.comments import InstagramPrivateReplyIneligibleError
from instagram_api.domain import (
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMessageId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateReplySource,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaHttpResponse, MetaTransientError
from tests.infrastructure.meta.comments.reply_factories import build_private_reply_provider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_request() -> InstagramPrivateCommentReplyRequest:
    return InstagramPrivateCommentReplyRequest(
        comment_id=InstagramCommentId("comment"),
        text="private reply",
        comment_created_at=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
        source=InstagramPrivateReplySource.STANDARD,
    )


def test_private_reply_provider_posts_comment_id_to_send_api() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                b'{"recipient_id":"recipient","message_id":"message"}',
            )
        ]
    )
    provider = build_private_reply_provider(transport, connection_id)

    result = asyncio.run(provider.reply(connection_id, build_request()))

    assert result.message_id == InstagramMessageId("message")
    assert result.recipient_id == InstagramUserId("recipient")
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/me/messages")
    assert request.json_body == {
        "recipient": {"comment_id": "comment"},
        "message": {"text": "private reply"},
    }
    assert request.headers["Authorization"] == "Bearer token"


def test_private_reply_provider_normalizes_ineligible_rejection() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                400,
                {},
                b'{"error":{"message":"private reply not eligible","code":10}}',
            )
        ]
    )
    provider = build_private_reply_provider(transport, connection_id)

    with pytest.raises(InstagramPrivateReplyIneligibleError):
        asyncio.run(provider.reply(connection_id, build_request()))


def test_private_reply_provider_never_retries_non_idempotent_post() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                500,
                {},
                b'{"error":{"message":"temporary","code":2}}',
            ),
            MetaHttpResponse(
                200,
                {},
                b'{"recipient_id":"recipient","message_id":"duplicate-risk"}',
            ),
        ]
    )
    provider = build_private_reply_provider(transport, connection_id)

    with pytest.raises(MetaTransientError):
        asyncio.run(provider.reply(connection_id, build_request()))

    assert len(transport.requests) == 1
