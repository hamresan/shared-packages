"""Instagram messaging read policy tests."""

import pytest

from instagram_api.application.messaging import (
    InstagramMessagingConnectionUnavailableError,
    InstagramMessagingPermissionRequiredError,
    InstagramMessagingReadPolicy,
)
from instagram_api.domain import InstagramAccountId, InstagramConnection, InstagramConnectionId


def test_policy_accepts_usable_connection_with_required_permissions() -> None:
    connection = InstagramConnection(
        id=InstagramConnectionId("connection"),
        provider_account_id=InstagramAccountId("account"),
        permissions=frozenset(
            {
                "instagram_business_basic",
                "instagram_business_manage_messages",
            }
        ),
        is_usable=True,
    )

    InstagramMessagingReadPolicy().validate_connection(connection)


@pytest.mark.parametrize(
    ("connection", "error_type"),
    [
        (
            InstagramConnection(
                id=InstagramConnectionId("connection"),
                provider_account_id=InstagramAccountId("account"),
                permissions=frozenset(
                    {
                        "instagram_business_basic",
                        "instagram_business_manage_messages",
                    }
                ),
                is_usable=False,
            ),
            InstagramMessagingConnectionUnavailableError,
        ),
        (
            InstagramConnection(
                id=InstagramConnectionId("connection"),
                provider_account_id=InstagramAccountId("account"),
                permissions=frozenset({"instagram_business_basic"}),
                is_usable=True,
            ),
            InstagramMessagingPermissionRequiredError,
        ),
        (
            InstagramConnection(
                id=InstagramConnectionId("connection"),
                provider_account_id=InstagramAccountId("account"),
                permissions=frozenset({"instagram_business_manage_messages"}),
                is_usable=True,
            ),
            InstagramMessagingPermissionRequiredError,
        ),
    ],
)
def test_policy_rejects_ineligible_connections(
    connection: InstagramConnection,
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        InstagramMessagingReadPolicy().validate_connection(connection)
