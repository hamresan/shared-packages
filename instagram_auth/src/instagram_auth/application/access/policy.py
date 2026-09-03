"""Fail-closed policy for downstream Instagram connection access."""

from collections.abc import Collection

from instagram_auth.application.errors.access import (
    InstagramConnectionPermissionError,
    InstagramConnectionUnavailableError,
)
from instagram_auth.baseline import InstagramConnectionState, InstagramPermission
from instagram_auth.domain import InstagramConnection


class InstagramConnectionAccessPolicy:
    """Validate whether one selected connection may serve downstream API access."""

    def validate(
        self,
        *,
        connection: InstagramConnection,
        required_permissions: Collection[InstagramPermission],
    ) -> None:
        if connection.status is not InstagramConnectionState.CONNECTED:
            raise InstagramConnectionUnavailableError("Instagram connection is not connected")
        if connection.revoked_at is not None:
            raise InstagramConnectionUnavailableError("Instagram connection credential is revoked")
        missing_permissions = frozenset(required_permissions) - connection.permissions
        if missing_permissions:
            raise InstagramConnectionPermissionError(
                "Instagram connection lacks required permissions"
            )
