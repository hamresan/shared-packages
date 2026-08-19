from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from identity.application.contracts.repositories import SessionRepository
from identity.domain import Session
from identity.infrastructure.persistence.sqlalchemy.mappers import SessionMapper
from identity.infrastructure.persistence.sqlalchemy.models import SessionModel


class SqlAlchemySessionRepository(SessionRepository):
    def __init__(self, session: AsyncSession, mapper: SessionMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get_by_refresh_token_hash(self, refresh_token_hash: str) -> Session | None:
        statement = select(SessionModel).where(
            SessionModel.refresh_token_hash == refresh_token_hash
        )
        model = await self._session.scalar(statement)
        return self._mapper.to_domain(model) if model is not None else None

    async def get_for_update_by_refresh_token_hash(
        self,
        refresh_token_hash: str,
    ) -> Session | None:
        statement = (
            select(SessionModel)
            .where(SessionModel.refresh_token_hash == refresh_token_hash)
            .with_for_update()
        )
        model = await self._session.scalar(statement)
        return self._mapper.to_domain(model) if model is not None else None

    async def revoke_family(self, family_id: UUID, revoked_at: datetime) -> None:
        statement = (
            update(SessionModel)
            .where(SessionModel.family_id == family_id, SessionModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self._session.execute(statement)

    async def add(self, session: Session) -> None:
        self._session.add(self._mapper.to_model(session))

    async def save(self, session: Session) -> None:
        await self._session.merge(self._mapper.to_model(session))
