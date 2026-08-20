from dataclasses import replace

from identity.application.contracts.security import Clock, SecretHasher
from identity.application.contracts.security_events import SecurityEvent, SecurityEventSink
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.errors import InvalidRefreshTokenError
from identity.application.factories.security_events import IdentitySecurityEventFactory


class RevokeSessionService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        hasher: SecretHasher,
        security_event_sink: SecurityEventSink,
        security_event_factory: IdentitySecurityEventFactory,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher
        self._security_event_sink = security_event_sink
        self._security_event_factory = security_event_factory

    async def execute(self, refresh_token: str) -> None:
        candidate_hashes = self._hasher.hash_candidates(refresh_token)
        event: SecurityEvent | None = None

        async with self._unit_of_work_factory() as uow:
            session = await uow.sessions.get_for_update_by_refresh_token_hashes(candidate_hashes)
            if session is None:
                raise InvalidRefreshTokenError("Refresh token is invalid")

            now = self._clock.now()
            if session.replaced_by_session_id is not None:
                await uow.sessions.revoke_family(session.family_id, now)
                await uow.commit()
                event = self._security_event_factory.session_revoked(
                    occurred_at=now,
                    session=session,
                )
            elif session.revoked_at is None:
                await uow.sessions.save(replace(session, revoked_at=now))
                await uow.commit()
                event = self._security_event_factory.session_revoked(
                    occurred_at=now,
                    session=session,
                )

        if event is not None:
            await self._security_event_sink.emit(event)
