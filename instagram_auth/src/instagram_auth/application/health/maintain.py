"""Host-invoked maintenance for one explicit Instagram connection."""

from collections.abc import Collection

from instagram_auth.application.contracts.clock import Clock
from instagram_auth.application.contracts.security_event_sink import InstagramSecurityEventSink
from instagram_auth.application.contracts.unit_of_work import InstagramAuthUnitOfWork
from instagram_auth.application.errors.connection_access import InstagramConnectionNotFoundError
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnectionId

from .event_factory import InstagramHealthSecurityEventFactory
from .models import InstagramConnectionHealth
from .policy import InstagramConnectionHealthPolicy
from .updater import InstagramConnectionHealthUpdater


class MaintainInstagramConnectionHealth:
    """Evaluate and persist health metadata for one selected connection only."""

    def __init__(
        self,
        unit_of_work: InstagramAuthUnitOfWork,
        clock: Clock,
        health_policy: InstagramConnectionHealthPolicy,
        connection_updater: InstagramConnectionHealthUpdater,
        security_event_factory: InstagramHealthSecurityEventFactory,
        security_event_sink: InstagramSecurityEventSink,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._clock = clock
        self._health_policy = health_policy
        self._connection_updater = connection_updater
        self._security_event_factory = security_event_factory
        self._security_event_sink = security_event_sink

    async def execute(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> InstagramConnectionHealth:
        now = self._clock.now()
        async with self._unit_of_work:
            connection = await self._unit_of_work.connections.get_by_id(connection_id)
            if connection is None:
                raise InstagramConnectionNotFoundError("Instagram connection not found")

            health = self._health_policy.evaluate(
                connection=connection,
                required_permissions=required_permissions,
                now=now,
            )
            updated = self._connection_updater.apply(
                connection=connection,
                health=health,
                validated_at=now,
            )
            await self._unit_of_work.connections.update(updated)
            await self._unit_of_work.commit()

        for event in self._security_event_factory.build(health):
            await self._security_event_sink.publish(event)
        return health
