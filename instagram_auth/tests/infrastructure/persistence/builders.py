from datetime import UTC, datetime
from uuid import UUID

from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId

NOW = datetime(2026, 9, 3, 14, 0, tzinfo=UTC)


def build_connection(
    *,
    connection_id: str,
    owner_user_id: str = "owner-1",
    instagram_account_id: str = "ig-1",
    username: str = "shop",
    version: int = 1,
) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId(UUID(connection_id)),
        owner_user_id=owner_user_id,
        instagram_account_id=instagram_account_id,
        username=username,
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW,
        version=version,
    )
