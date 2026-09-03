from asyncio import run
from datetime import UTC, datetime
from uuid import UUID

from instagram_auth.application.permissions import (
    ApplyInstagramPermissionSnapshot,
    InstagramPermissionPolicy,
)
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from tests.application.permissions.fakes import FakeInstagramConnectionRepository

NOW = datetime(2026, 9, 3, tzinfo=UTC)


def build_connection(value: str, account_id: str) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId(UUID(value)),
        owner_user_id="owner-1",
        instagram_account_id=account_id,
        username=account_id,
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW,
    )


def test_partial_snapshot_marks_only_selected_connection_for_reauthorization() -> None:
    first = build_connection("00000000-0000-0000-0000-000000000001", "ig-1")
    second = build_connection("00000000-0000-0000-0000-000000000002", "ig-2")
    repository = FakeInstagramConnectionRepository((first, second))
    service = ApplyInstagramPermissionSnapshot(repository, InstagramPermissionPolicy())

    result = run(
        service.execute(
            connection_id=first.id,
            required_permissions=frozenset(
                {InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES}
            ),
            granted_permissions=frozenset({InstagramPermission.BASIC}),
        )
    )

    assert result.requires_reauthorization is True
    assert (
        repository.connections[first.id].status is InstagramConnectionState.REAUTHORIZATION_REQUIRED
    )
    assert repository.connections[second.id] == second


def test_complete_reauthorization_restores_selected_connection() -> None:
    connection = build_connection("00000000-0000-0000-0000-000000000003", "ig-3")
    repository = FakeInstagramConnectionRepository((connection,))
    service = ApplyInstagramPermissionSnapshot(repository, InstagramPermissionPolicy())
    granted = frozenset({InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES})

    result = run(
        service.execute(
            connection_id=connection.id,
            required_permissions=granted,
            granted_permissions=granted,
        )
    )

    assert result.requires_reauthorization is False
    assert repository.connections[connection.id].status is InstagramConnectionState.CONNECTED
    assert repository.connections[connection.id].permissions == granted
