"""Instagram public and private comment reply service tests."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.application.comments import (
    InstagramCommentReplyAccessPolicy,
    InstagramCommentReplyTextPolicy,
    InstagramPrivateCommentReplyService,
    InstagramPrivateReplyEligibilityPolicy,
    InstagramPrivateReplyLiveInactiveError,
    InstagramPublicCommentReplyService,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramCommentId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateReplySource,
)
from tests.fakes import (
    FakeInstagramConnectionReader,
    FakeInstagramPrivateCommentReplyProvider,
    FakeInstagramPublicCommentReplyProvider,
    FixedInstagramReplyClock,
)

NOW = datetime(2026, 9, 4, 12, 0, tzinfo=UTC)


def build_connections() -> dict[InstagramConnectionId, InstagramConnection]:
    permissions = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_comments",
        }
    )
    first_id = InstagramConnectionId("connection-a")
    second_id = InstagramConnectionId("connection-b")
    return {
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


def test_public_reply_service_routes_selected_connection() -> None:
    connections = build_connections()
    connection_id = InstagramConnectionId("connection-a")
    comment_id = InstagramCommentId("comment")
    provider = FakeInstagramPublicCommentReplyProvider()
    service = InstagramPublicCommentReplyService(
        FakeInstagramConnectionReader(connections),
        provider,
        InstagramCommentReplyAccessPolicy(),
        InstagramCommentReplyTextPolicy(),
    )

    result = asyncio.run(service.reply_publicly(connection_id, comment_id, "public reply"))

    assert result.comment_id == InstagramCommentId("public-reply")
    assert provider.calls == [(connection_id, comment_id, "public reply")]


def test_private_reply_service_routes_selected_connection_after_eligibility() -> None:
    connections = build_connections()
    connection_id = InstagramConnectionId("connection-b")
    provider = FakeInstagramPrivateCommentReplyProvider()
    request = InstagramPrivateCommentReplyRequest(
        comment_id=InstagramCommentId("comment"),
        text="private reply",
        comment_created_at=NOW,
        source=InstagramPrivateReplySource.STANDARD,
    )
    service = InstagramPrivateCommentReplyService(
        FakeInstagramConnectionReader(connections),
        provider,
        InstagramCommentReplyAccessPolicy(),
        InstagramCommentReplyTextPolicy(),
        InstagramPrivateReplyEligibilityPolicy(FixedInstagramReplyClock(NOW)),
    )

    result = asyncio.run(service.reply_privately(connection_id, request))

    assert result.message_id is not None
    assert provider.calls == [(connection_id, request)]


def test_private_reply_service_rejects_ineligible_live_before_provider_call() -> None:
    connections = build_connections()
    connection_id = InstagramConnectionId("connection-a")
    provider = FakeInstagramPrivateCommentReplyProvider()
    request = InstagramPrivateCommentReplyRequest(
        comment_id=InstagramCommentId("live-comment"),
        text="private reply",
        comment_created_at=NOW,
        source=InstagramPrivateReplySource.LIVE,
        live_is_active=False,
    )
    service = InstagramPrivateCommentReplyService(
        FakeInstagramConnectionReader(connections),
        provider,
        InstagramCommentReplyAccessPolicy(),
        InstagramCommentReplyTextPolicy(),
        InstagramPrivateReplyEligibilityPolicy(FixedInstagramReplyClock(NOW)),
    )

    with pytest.raises(InstagramPrivateReplyLiveInactiveError):
        asyncio.run(service.reply_privately(connection_id, request))

    assert provider.calls == []
