"""Verify host-observable security events stay normalized and secret-free."""

from uuid import UUID

from instagram_auth.application.health.event_factory import InstagramHealthSecurityEventFactory
from instagram_auth.application.health.models import (
    InstagramConnectionHealth,
    InstagramConnectionHealthReason,
    InstagramConnectionHealthStatus,
)
from instagram_auth.application.models import InstagramSecurityEventKind
from instagram_auth.domain import InstagramConnectionId


def test_health_security_events_expose_only_normalized_non_secret_context() -> None:
    connection_id = InstagramConnectionId(UUID("00000000-0000-0000-0000-000000000701"))
    health = InstagramConnectionHealth(
        connection_id=connection_id,
        status=InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED,
        reasons=frozenset(
            {
                InstagramConnectionHealthReason.REVOKED_CREDENTIAL,
                InstagramConnectionHealthReason.MISSING_PERMISSION,
            }
        ),
    )

    events = InstagramHealthSecurityEventFactory().build(health)

    assert {event.kind for event in events} == {
        InstagramSecurityEventKind.CREDENTIAL_REVOKED,
        InstagramSecurityEventKind.PERMISSION_LOSS,
    }
    assert all(event.connection_id == connection_id for event in events)
    assert "token" not in repr(events).lower()
    assert "secret" not in repr(events).lower()
