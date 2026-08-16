from dataclasses import replace

from identity.application.contracts.security import Clock, SecretHasher
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.errors import InvalidRefreshTokenError


class RevokeSessionService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        hasher: SecretHasher,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher

    async def execute(self, refresh_token: str) -> None:
        async with self._unit_of_work_factory() as uow:
            session = await uow.sessions.get_by_refresh_token_hash(self._hasher.hash(refresh_token))
            if session is None:
                raise InvalidRefreshTokenError("Refresh token is invalid")
            if session.revoked_at is None:
                await uow.sessions.save(replace(session, revoked_at=self._clock.now()))
                await uow.commit()
