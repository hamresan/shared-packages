"""Instagram comment access policy tests."""

import pytest

from instagram_api.application.comments import (
    InstagramCommentAccessPolicy,
    InstagramCommentConnectionUnavailableError,
    InstagramCommentPermissionRequiredError,
)
from instagram_api.domain import InstagramAccountId, InstagramConnection, InstagramConnectionId


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


def test_comment_access_policy_accepts_required_permissions() -> None:
    InstagramCommentAccessPolicy().validate_connection(build_connection())


@pytest.mark.parametrize(
    ("connection", "error_type"),
    [
        (
            build_connection(usable=False),
            InstagramCommentConnectionUnavailableError,
        ),
        (
            build_connection(
                permissions=frozenset({"instagram_business_manage_comments"})
            ),
            InstagramCommentPermissionRequiredError,
        ),
        (
            build_connection(permissions=frozenset({"instagram_business_basic"})),
            InstagramCommentPermissionRequiredError,
        ),
    ],
)
def test_comment_access_policy_rejects_ineligible_connection(
    connection: InstagramConnection,
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        InstagramCommentAccessPolicy().validate_connection(connection)
