from uuid import UUID

from identity.application.contracts.security import Clock
from identity.application.contracts.security_events import SecurityEventSink
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.factories.security_events import IdentitySecurityEventFactory


class RevokeAllSessionsService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        security_event_sink: SecurityEventSink,
        security_event_factory: IdentitySecurityEventFactory,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._security_event_sink = security_event_sink
        self._security_event_factory = security_event_factory

    async def execute(self, user_id: UUID) -> None:
        now = self._clock.now()
        async with self._unit_of_work_factory() as uow:
            await uow.sessions.revoke_all_by_user_id(user_id, now)
            await uow.commit()

        await self._security_event_sink.emit(
            self._security_event_factory.sessions_revoked_all(
                occurred_at=now,
                user_id=user_id,
            )
        )
