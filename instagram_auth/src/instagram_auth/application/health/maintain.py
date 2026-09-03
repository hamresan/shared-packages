"""Host-invoked maintenance for one explicit Instagram connection."""

from collections.abc import Collection
from dataclasses import replace

from instagram_auth.application.contracts.clock import Clock
from instagram_auth.application.contracts.security_event_sink import InstagramSecurityEventSink
from instagram_auth.application.contracts.unit_of_work import InstagramAuthUnitOfWork
from instagram_auth.application.errors.connection_access import InstagramConnectionNotFoundError
from instagram_auth.baseline import InstagramConnectionState, InstagramPermission
from instagram_auth.domain import InstagramConnection, InstagramConnectionId

from .models import (
    InstagramConnectionHealth,
    InstagramConnectionHealthReason,
    InstagramConnectionHealthStatus,
    InstagramSecurityEvent,
    InstagramSecurityEventKind,
)
from .policy import InstagramConnectionHealthPolicy


class MaintainInstagramConnectionHealth:
    """Evaluate and persist health metadata for one selected connection only."""

    def __init__(
        self,
        unit_of_work: InstagramAuthUnitOfWork,
        clock: Clock,
        health_policy: InstagramConnectionHealthPolicy,
        security_event_sink: InstagramSecurityEventSink,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._clock = clock
        self._health_policy = health_policy
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
            updated = self._build_updated_connection(connection, health, now)
            await self._unit_of_work.connections.update(updated)
            await self._unit_of_work.commit()

        for event in self._security_events(health):
            await self._security_event_sink.publish(event)
        return health

    @staticmethod
    def _build_updated_connection(
        connection: InstagramConnection,
        health: InstagramConnectionHealth,
        now: object,
    ) -> InstagramConnection:
        status = connection.status
        if health.status is InstagramConnectionHealthStatus.REAUTHORIZATION_REQUIRED:
            status = InstagramConnectionState.REAUTHORIZATION_REQUIRED
        return replace(connection, status=status, last_validated_at=now)

    @staticmethod
    def _security_events(health: InstagramConnectionHealth) -> tuple[InstagramSecurityEvent, ...]:
        events: list[InstagramSecurityEvent] = []
        mapping = {
            InstagramConnectionHealthReason.EXPIRED_CREDENTIAL: InstagramSecurityEventKind.CREDENTIAL_EXPIRED,
            InstagramConnectionHealthReason.REVOKED_CREDENTIAL: InstagramSecurityEventKind.CREDENTIAL_REVOKED,
            InstagramConnectionHealthReason.MISSING_PERMISSION: InstagramSecurityEventKind.PERMISSION_LOSS,
        }
        for reason, kind in mapping.items():
            if reason in health.reasons:
                events.append(InstagramSecurityEvent(connection_id=health.connection_id, kind=kind))
        return tuple(events)
