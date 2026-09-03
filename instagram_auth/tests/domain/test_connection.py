from datetime import UTC, datetime
from uuid import UUID

from instagram_auth.baseline import (
    CORE_PERMISSIONS,
    InstagramAccountType,
    InstagramConnectionState,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId


def test_same_owner_can_have_multiple_independent_connections() -> None:
    connected_at = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
    first = InstagramConnection(
        id=InstagramConnectionId(UUID("11111111-1111-1111-1111-111111111111")),
        owner_user_id="host-user-42",
        instagram_account_id="instagram-account-a",
        username="store_a",
        account_type=InstagramAccountType.BUSINESS,
        permissions=CORE_PERMISSIONS,
        status=InstagramConnectionState.CONNECTED,
        connected_at=connected_at,
    )
    second = InstagramConnection(
        id=InstagramConnectionId(UUID("22222222-2222-2222-2222-222222222222")),
        owner_user_id="host-user-42",
        instagram_account_id="instagram-account-b",
        username="store_b",
        account_type=InstagramAccountType.CREATOR,
        permissions=CORE_PERMISSIONS,
        status=InstagramConnectionState.CONNECTED,
        connected_at=connected_at,
    )

    assert first.owner_user_id == second.owner_user_id
    assert first.id != second.id
    assert first.instagram_account_id != second.instagram_account_id
