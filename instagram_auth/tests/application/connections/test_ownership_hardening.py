"""Additional authorization tests for connection-management mutations."""

from asyncio import run
from datetime import UTC, datetime
from uuid import UUID

import pytest

from instagram_auth.application.connections import (
    DisconnectInstagramConnection,
    InstagramConnectionOwnershipPolicy,
    ReconnectInstagramConnection,
)
from instagram_auth.application.errors.connection_access import (
    InstagramConnectionNotFoundError,
    InstagramConnectionOwnershipError,
)
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from tests.application.connections.fakes import FakeConnectionStore, FakeInstagramAuthUnitOfWork

NOW = datetime(2026, 9, 4, tzinfo=UTC)


def build_connection(value: int, owner_user_id: str) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId(UUID(int=value)),
        owner_user_id=owner_user_id,
        instagram_account_id=f"ig-{value}",
        username=f"account-{value}",
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW,
    )


def test_reconnect_rejects_cross_owner_mutation_without_commit() -> None:
    connection = build_connection(601, "owner-1")
    store = FakeConnectionStore((connection,))
    unit_of_work = FakeInstagramAuthUnitOfWork(store)

    with pytest.raises(InstagramConnectionOwnershipError):
        run(
            ReconnectInstagramConnection(
                unit_of_work,
                InstagramConnectionOwnershipPolicy(),
            ).execute(owner_user_id="owner-2", connection_id=connection.id)
        )

    assert store.connections[connection.id] == connection
    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 1


def test_disconnect_missing_connection_does_not_commit() -> None:
    store = FakeConnectionStore()
    unit_of_work = FakeInstagramAuthUnitOfWork(store)

    with pytest.raises(InstagramConnectionNotFoundError):
        run(
            DisconnectInstagramConnection(
                unit_of_work,
                InstagramConnectionOwnershipPolicy(),
            ).execute(
                owner_user_id="owner-1",
                connection_id=InstagramConnectionId(UUID(int=602)),
            )
        )

    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 1
