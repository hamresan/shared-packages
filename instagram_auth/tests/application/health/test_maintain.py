"""Host-invoked connection-health maintenance tests."""

from asyncio import run
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

from instagram_auth.application.health import (
    InstagramConnectionHealthPolicy,
    InstagramConnectionHealthStatus,
    InstagramConnectionHealthUpdater,
    InstagramHealthSecurityEventFactory,
    MaintainInstagramConnectionHealth,
)
from instagram_auth.application.models import InstagramSecurityEventKind
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from tests.application.connections.fakes import FakeConnectionStore, FakeInstagramAuthUnitOfWork
from tests.application.contracts.fakes import FixedClock
from tests.application.health.fakes import FakeInstagramSecurityEventSink

NOW = datetime(2026, 9, 4, tzinfo=UTC)


def build_connection(value: int, *, owner_user_id: str = "owner-1") -> InstagramConnection:
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


def build_maintenance(
    store: FakeConnectionStore,
    event_sink: FakeInstagramSecurityEventSink,
) -> MaintainInstagramConnectionHealth:
    return MaintainInstagramConnectionHealth(
        unit_of_work=FakeInstagramAuthUnitOfWork(store),
        clock=FixedClock(NOW),
        health_policy=InstagramConnectionHealthPolicy(),
        connection_updater=InstagramConnectionHealthUpdater(),
        security_event_factory=InstagramHealthSecurityEventFactory(),
        security_event_sink=event_sink,
    )


def test_maintenance_marks_only_expired_selected_connection_for_reauthorization() -> None:
    expired = replace(
        build_connection(11),
        credential_expires_at=NOW - timedelta(seconds=1),
    )
    sibling = build_connection(12)
    store = FakeConnectionStore((expired, sibling))
    event_sink = FakeInstagramSecurityEventSink()

    health = run(build_maintenance(store, event_sink).execute(connection_id=expired.id))

    assert health.status is InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED
    assert store.connections[expired.id].status is InstagramConnectionState.REAUTHORIZATION_REQUIRED
    assert store.connections[expired.id].last_validated_at == NOW
    assert store.connections[sibling.id] == sibling
    assert [event.kind for event in event_sink.events] == [
        InstagramSecurityEventKind.CREDENTIAL_EXPIRED
    ]


def test_maintenance_emits_permission_loss_without_affecting_sibling_connection() -> None:
    selected = build_connection(13)
    sibling = build_connection(14)
    store = FakeConnectionStore((selected, sibling))
    event_sink = FakeInstagramSecurityEventSink()

    health = run(
        build_maintenance(store, event_sink).execute(
            connection_id=selected.id,
            required_permissions=(InstagramPermission.MANAGE_MESSAGES,),
        )
    )

    assert health.status is InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED
    assert store.connections[sibling.id] == sibling
    assert [event.kind for event in event_sink.events] == [
        InstagramSecurityEventKind.PERMISSION_LOSS
    ]
