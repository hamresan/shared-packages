"""Instagram comment reply policy tests."""

from datetime import UTC, datetime, timedelta

import pytest

from instagram_api.application.comments import (
    InstagramCommentConnectionUnavailableError,
    InstagramCommentPermissionRequiredError,
    InstagramCommentReplyAccessPolicy,
    InstagramCommentReplyPayloadInvalidError,
    InstagramCommentReplyTextPolicy,
    InstagramPrivateReplyEligibilityPolicy,
    InstagramPrivateReplyExpiredError,
    InstagramPrivateReplyLiveInactiveError,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramCommentId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateReplySource,
)
from tests.fakes import FixedInstagramReplyClock

NOW = datetime(2026, 9, 4, 12, 0, tzinfo=UTC)


def build_connection(
    *,
    usable: bool = True,
    permissions: frozenset[str] = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_comments",
        }
    ),
) -> InstagramConnection:
    return InstagramConnection(
        InstagramConnectionId("connection"),
        InstagramAccountId("account"),
        permissions,
        usable,
    )


def standard_request(created_at: datetime) -> InstagramPrivateCommentReplyRequest:
    return InstagramPrivateCommentReplyRequest(
        comment_id=InstagramCommentId("comment"),
        text="private reply",
        comment_created_at=created_at,
        source=InstagramPrivateReplySource.STANDARD,
    )


def test_reply_access_policy_accepts_required_permissions() -> None:
    InstagramCommentReplyAccessPolicy().validate_connection(build_connection())


@pytest.mark.parametrize(
    ("connection", "error_type"),
    [
        (
            build_connection(usable=False),
            InstagramCommentConnectionUnavailableError,
        ),
        (
            build_connection(permissions=frozenset({"instagram_business_manage_comments"})),
            InstagramCommentPermissionRequiredError,
        ),
        (
            build_connection(permissions=frozenset({"instagram_business_basic"})),
            InstagramCommentPermissionRequiredError,
        ),
    ],
)
def test_reply_access_policy_rejects_ineligible_connection(
    connection: InstagramConnection,
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        InstagramCommentReplyAccessPolicy().validate_connection(connection)


def test_reply_text_policy_rejects_blank_text() -> None:
    with pytest.raises(InstagramCommentReplyPayloadInvalidError):
        InstagramCommentReplyTextPolicy().validate("   ")


def test_standard_private_reply_allows_exact_seven_day_boundary() -> None:
    policy = InstagramPrivateReplyEligibilityPolicy(FixedInstagramReplyClock(NOW))

    policy.validate(standard_request(NOW - timedelta(days=7)))


def test_standard_private_reply_rejects_expired_and_future_comment() -> None:
    policy = InstagramPrivateReplyEligibilityPolicy(FixedInstagramReplyClock(NOW))

    with pytest.raises(InstagramPrivateReplyExpiredError):
        policy.validate(standard_request(NOW - timedelta(days=7, seconds=1)))

    with pytest.raises(InstagramPrivateReplyExpiredError):
        policy.validate(standard_request(NOW + timedelta(seconds=1)))


def test_live_private_reply_requires_active_broadcast() -> None:
    policy = InstagramPrivateReplyEligibilityPolicy(FixedInstagramReplyClock(NOW))

    active_request = InstagramPrivateCommentReplyRequest(
        comment_id=InstagramCommentId("live-comment"),
        text="private reply",
        comment_created_at=NOW - timedelta(days=30),
        source=InstagramPrivateReplySource.LIVE,
        live_is_active=True,
    )
    inactive_request = InstagramPrivateCommentReplyRequest(
        comment_id=InstagramCommentId("live-comment"),
        text="private reply",
        comment_created_at=NOW,
        source=InstagramPrivateReplySource.LIVE,
        live_is_active=False,
    )

    policy.validate(active_request)

    with pytest.raises(InstagramPrivateReplyLiveInactiveError):
        policy.validate(inactive_request)
