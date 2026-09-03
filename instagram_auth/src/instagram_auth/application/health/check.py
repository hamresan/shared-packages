"""Read-only health check for one explicit Instagram connection."""

from collections.abc import Collection

from instagram_auth.application.contracts.clock import Clock
from instagram_auth.application.contracts.connection_reader import InstagramConnectionReader
from instagram_auth.application.errors.access import InstagramConnectionUnavailableError
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnectionId

from .models import InstagramConnectionHealth
from .policy import InstagramConnectionHealthPolicy


class CheckInstagramConnectionHealth:
    """Return explicit health for one selected connection."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        clock: Clock,
        health_policy: InstagramConnectionHealthPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._clock = clock
        self._health_policy = health_policy

    async def execute(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> InstagramConnectionHealth:
        connection = await self._connection_reader.get(connection_id)
        if connection is None:
            raise InstagramConnectionUnavailableError("Instagram connection not found")
        return self._health_policy.evaluate(
            connection=connection,
            required_permissions=required_permissions,
            now=self._clock.now(),
        )
