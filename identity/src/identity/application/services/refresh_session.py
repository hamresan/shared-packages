from dataclasses import replace

from identity.application.contracts.security import (
    AccessTokenIssuer,
    Clock,
    RefreshTokenGenerator,
    SecretHasher,
)
from identity.application.contracts.security_event_factory import SecurityEventFactory
from identity.application.contracts.security_events import SecurityEventSink
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import AuthSessionResult, RefreshSessionCommand
from identity.application.errors import InvalidRefreshTokenError, RefreshTokenReuseError
from identity.application.factories.entities import SessionFactory


class RefreshSessionService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        hasher: SecretHasher,
        refresh_token_generator: RefreshTokenGenerator,
        access_token_issuer: AccessTokenIssuer,
        session_factory: SessionFactory,
        security_event_sink: SecurityEventSink,
        security_event_factory: SecurityEventFactory,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher
        self._refresh_token_generator = refresh_token_generator
        self._access_token_issuer = access_token_issuer
        self._session_factory = session_factory
        self._security_event_sink = security_event_sink
        self._security_event_factory = security_event_factory

    async def execute(self, command: RefreshSessionCommand) -> AuthSessionResult:
        now = self._clock.now()
        candidate_hashes = self._hasher.hash_candidates(command.refresh_token)
        async with self._unit_of_work_factory() as uow:
            current = await uow.sessions.get_for_update_by_refresh_token_hashes(candidate_hashes)
            if current is None or current.expires_at <= now or current.family_expires_at <= now:
                raise InvalidRefreshTokenError("Refresh token is invalid")

            if current.revoked_at is not None:
                if current.replaced_by_session_id is not None:
                    await uow.sessions.revoke_family(current.family_id, now)
                    await uow.commit()
                    await self._security_event_sink.emit(
                        self._security_event_factory.refresh_reuse_detected(
                            occurred_at=now,
                            session=current,
                        )
                    )
                    raise RefreshTokenReuseError("Refresh token reuse detected")
                raise InvalidRefreshTokenError("Refresh token is invalid")

            refresh_token = self._refresh_token_generator.generate()
            replacement = self._session_factory.create(
                now=now,
                user_id=current.user_id,
                refresh_token_hash=self._hasher.hash(refresh_token),
                device_info=command.device_info or current.device_info,
                ip_address=command.ip_address or current.ip_address,
                family_id=current.family_id,
                parent_session_id=current.id,
                family_expires_at=current.family_expires_at,
            )
            access_token = await self._access_token_issuer.issue(
                replacement.user_id,
                replacement.id,
            )
            await uow.sessions.add(replacement)
            await uow.sessions.save(
                replace(
                    current,
                    revoked_at=now,
                    replaced_by_session_id=replacement.id,
                    last_used_at=now,
                )
            )
            await uow.commit()

        return AuthSessionResult(
            user_id=replacement.user_id,
            session_id=replacement.id,
            access_token=access_token.token,
            access_token_expires_at=access_token.expires_at,
            refresh_token=refresh_token,
            refresh_token_expires_at=replacement.expires_at,
        )
