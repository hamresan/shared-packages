"""Connection-health evaluation policy."""

from collections.abc import Collection
from datetime import datetime

from instagram_auth.baseline import InstagramConnectionState, InstagramPermission
from instagram_auth.domain import InstagramConnection

from .models import (
    InstagramConnectionHealth,
    InstagramConnectionHealthReason,
    InstagramConnectionHealthStatus,
)


class InstagramConnectionHealthPolicy:
    """Evaluate one connection without mutating persistence or calling providers."""

    def evaluate(
        self,
        *,
        connection: InstagramConnection,
        required_permissions: Collection[InstagramPermission] = (),
        now: datetime,
    ) -> InstagramConnectionHealth:
        if connection.status is InstagramConnectionState.DISCONNECTED:
            return InstagramConnectionHealth(
                connection_id=connection.id,
                status=InstagramConnectionHealthStatus.DISCONNECTED,
                reasons=frozenset({InstagramConnectionHealthReason.CONNECTION_STATUS}),
            )

        reasons: set[InstagramConnectionHealthReason] = set()
        if connection.revoked_at is not None:
            reasons.add(InstagramConnectionHealthReason.REVOKED_CREDENTIAL)
        if connection.credential_expires_at is not None and connection.credential_expires_at <= now:
            reasons.add(InstagramConnectionHealthReason.EXPIRED_CREDENTIAL)

        missing_permissions = frozenset(required_permissions) - connection.permissions
        if missing_permissions:
            reasons.add(InstagramConnectionHealthReason.MISSING_PERMISSION)

        if connection.status is not InstagramConnectionState.CONNECTED:
            reasons.add(InstagramConnectionHealthReason.CONNECTION_STATUS)

        if reasons:
            return InstagramConnectionHealth(
                connection_id=connection.id,
                status=InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED,
                reasons=frozenset(reasons),
                missing_permissions=missing_permissions,
            )

        return InstagramConnectionHealth(
            connection_id=connection.id,
            status=InstagramConnectionHealthStatus.USABLE,
        )
