"""Fail-closed policy for downstream Instagram connection access."""

from collections.abc import Collection

from instagram_auth.application.contracts.clock import Clock
from instagram_auth.application.errors.access import (
    InstagramConnectionPermissionError,
    InstagramConnectionUnavailableError,
)
from instagram_auth.application.health.models import InstagramConnectionHealthStatus
from instagram_auth.application.health.policy import InstagramConnectionHealthPolicy
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnection


class InstagramConnectionAccessPolicy:
    """Validate whether one selected connection may serve downstream API access."""

    def __init__(self, clock: Clock, health_policy: InstagramConnectionHealthPolicy) -> None:
        self._clock = clock
        self._health_policy = health_policy

    def validate(
        self,
        *,
        connection: InstagramConnection,
        required_permissions: Collection[InstagramPermission],
    ) -> None:
        health = self._health_policy.evaluate(
            connection=connection,
            required_permissions=required_permissions,
            now=self._clock.now(),
        )
        if health.missing_permissions:
            raise InstagramConnectionPermissionError(
                "Instagram connection lacks required permissions"
            )
        if health.status is not InstagramConnectionHealthStatus.USABLE:
            raise InstagramConnectionUnavailableError(
                "Instagram connection requires reauthorization or is disconnected"
            )
