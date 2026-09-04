"""Connection mutation component for health maintenance."""

from dataclasses import replace
from datetime import datetime

from instagram_auth.baseline import InstagramConnectionState
from instagram_auth.domain import InstagramConnection

from .models import InstagramConnectionHealth, InstagramConnectionHealthStatus


class InstagramConnectionHealthUpdater:
    """Build a persisted connection snapshot from a health evaluation."""

    def apply(
        self,
        *,
        connection: InstagramConnection,
        health: InstagramConnectionHealth,
        validated_at: datetime,
    ) -> InstagramConnection:
        status = connection.status
        if health.status is InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED:
            status = InstagramConnectionState.REAUTHORIZATION_REQUIRED
        return replace(connection, status=status, last_validated_at=validated_at)
