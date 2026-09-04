"""Connection-health policy tests."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

from instagram_auth.application.health import (
    InstagramConnectionHealthPolicy,
    InstagramConnectionHealthReason,
    InstagramConnectionHealthStatus,
)
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId

NOW = datetime(2026, 9, 4, tzinfo=UTC)


def build_connection(value: int) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId(UUID(int=value)),
        owner_user_id="owner-1",
        instagram_account_id=f"ig-{value}",
        username=f"account-{value}",
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW,
    )


def test_health_policy_marks_healthy_connection_usable() -> None:
    health = InstagramConnectionHealthPolicy().evaluate(
        connection=build_connection(1),
        required_permissions=(InstagramPermission.MANAGE_MESSAGES,),
        now=NOW,
    )

    assert health.status is InstagramConnectionHealthStatus.USABLE
    assert health.reasons == frozenset()


def test_health_policy_detects_expired_credential() -> None:
    connection = replace(build_connection(2), credential_expires_at=NOW - timedelta(seconds=1))

    health = InstagramConnectionHealthPolicy().evaluate(connection=connection, now=NOW)

    assert health.status is InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED
    assert InstagramConnectionHealthReason.EXPIRED_CREDENTIAL in health.reasons


def test_health_policy_detects_revocation_and_permission_loss() -> None:
    connection = replace(build_connection(3), revoked_at=NOW)

    health = InstagramConnectionHealthPolicy().evaluate(
        connection=connection,
        required_permissions=(InstagramPermission.CONTENT_PUBLISH,),
        now=NOW,
    )

    assert health.status is InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED
    assert health.missing_permissions == frozenset({InstagramPermission.CONTENT_PUBLISH})
    assert health.reasons == frozenset(
        {
            InstagramConnectionHealthReason.REVOKED_CREDENTIAL,
            InstagramConnectionHealthReason.MISSING_PERMISSION,
        }
    )


def test_health_policy_preserves_explicit_disconnected_state() -> None:
    connection = replace(build_connection(4), status=InstagramConnectionState.DISCONNECTED)

    health = InstagramConnectionHealthPolicy().evaluate(connection=connection, now=NOW)

    assert health.status is InstagramConnectionHealthStatus.DISCONNECTED
    assert health.reasons == frozenset({InstagramConnectionHealthReason.CONNECTION_STATUS})
