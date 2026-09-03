"""Connection-management application tests."""

from asyncio import run
from datetime import UTC, datetime
from uuid import UUID

import pytest

from instagram_auth.application.connections import (
    DisconnectInstagramConnection,
    GetInstagramConnection,
    InstagramConnectionOwnershipPolicy,
    ListInstagramConnections,
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

NOW = datetime(2026, 9, 3, tzinfo=UTC)


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


def test_list_returns_only_connections_owned_by_requested_user() -> None:
    first = build_connection(1, "owner-1")
    second = build_connection(2, "owner-1")
    other = build_connection(3, "owner-2")
    store = FakeConnectionStore((first, second, other))

    result = run(ListInstagramConnections(store).execute(owner_user_id="owner-1"))

    assert set(result) == {first, second}


def test_get_rejects_cross_owner_access() -> None:
    connection = build_connection(4, "owner-1")
    service = GetInstagramConnection(
        FakeConnectionStore((connection,)),
        InstagramConnectionOwnershipPolicy(),
    )

    with pytest.raises(InstagramConnectionOwnershipError):
        run(service.execute(owner_user_id="owner-2", connection_id=connection.id))


def test_get_reports_missing_connection() -> None:
    service = GetInstagramConnection(
        FakeConnectionStore(),
        InstagramConnectionOwnershipPolicy(),
    )

    with pytest.raises(InstagramConnectionNotFoundError):
        run(
            service.execute(
                owner_user_id="owner-1",
                connection_id=InstagramConnectionId(UUID(int=5)),
            )
        )


def test_disconnect_changes_only_selected_connection() -> None:
    first = build_connection(6, "owner-1")
    second = build_connection(7, "owner-1")
    store = FakeConnectionStore((first, second))
    unit_of_work = FakeInstagramAuthUnitOfWork(store)
    service = DisconnectInstagramConnection(
        unit_of_work,
        InstagramConnectionOwnershipPolicy(),
    )

    result = run(service.execute(owner_user_id="owner-1", connection_id=first.id))

    assert result.status is InstagramConnectionState.DISCONNECTED
    assert store.connections[first.id].status is InstagramConnectionState.DISCONNECTED
    assert store.connections[second.id] == second
    assert unit_of_work.commits == 1


def test_disconnect_rejects_cross_owner_mutation_without_commit() -> None:
    connection = build_connection(8, "owner-1")
    store = FakeConnectionStore((connection,))
    unit_of_work = FakeInstagramAuthUnitOfWork(store)
    service = DisconnectInstagramConnection(
        unit_of_work,
        InstagramConnectionOwnershipPolicy(),
    )

    with pytest.raises(InstagramConnectionOwnershipError):
        run(service.execute(owner_user_id="owner-2", connection_id=connection.id))

    assert store.connections[connection.id] == connection
    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 1


def test_reconnect_updates_selected_connection_in_place() -> None:
    connection = build_connection(9, "owner-1")
    store = FakeConnectionStore((connection,))
    unit_of_work = FakeInstagramAuthUnitOfWork(store)
    service = ReconnectInstagramConnection(
        unit_of_work,
        InstagramConnectionOwnershipPolicy(),
    )

    result = run(service.execute(owner_user_id="owner-1", connection_id=connection.id))

    assert result.id == connection.id
    assert result.instagram_account_id == connection.instagram_account_id
    assert result.status is InstagramConnectionState.AUTHORIZING
    assert len(store.connections) == 1
    assert unit_of_work.commits == 1


def test_reconnect_reports_missing_connection() -> None:
    service = ReconnectInstagramConnection(
        FakeInstagramAuthUnitOfWork(FakeConnectionStore()),
        InstagramConnectionOwnershipPolicy(),
    )

    with pytest.raises(InstagramConnectionNotFoundError):
        run(
            service.execute(
                owner_user_id="owner-1",
                connection_id=InstagramConnectionId(UUID(int=10)),
            )
        )
