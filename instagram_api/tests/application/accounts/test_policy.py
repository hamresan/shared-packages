"""Instagram account access policy tests."""

import pytest

from instagram_api.application.accounts import (
    InstagramAccountAccessPolicy,
    InstagramAccountMismatchError,
    InstagramConnectionUnavailableError,
    InstagramPermissionRequiredError,
)
from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
)


def build_connection(
    *,
    is_usable: bool = True,
    permissions: frozenset[str] = frozenset({"instagram_business_basic"}),
) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId("connection"),
        provider_account_id=InstagramAccountId("ig-account"),
        permissions=permissions,
        is_usable=is_usable,
    )


def test_policy_accepts_usable_connection_with_basic_permission() -> None:
    policy = InstagramAccountAccessPolicy()

    policy.validate_connection(build_connection())


def test_policy_rejects_unusable_connection() -> None:
    policy = InstagramAccountAccessPolicy()

    with pytest.raises(InstagramConnectionUnavailableError):
        policy.validate_connection(build_connection(is_usable=False))


def test_policy_rejects_missing_basic_permission() -> None:
    policy = InstagramAccountAccessPolicy()

    with pytest.raises(InstagramPermissionRequiredError):
        policy.validate_connection(build_connection(permissions=frozenset()))


def test_policy_rejects_provider_account_mismatch() -> None:
    policy = InstagramAccountAccessPolicy()
    connection = build_connection()
    account = InstagramAccount(
        id=InstagramAccountId("different-account"),
        username="shop",
    )

    with pytest.raises(InstagramAccountMismatchError):
        policy.validate_account(connection, account)
