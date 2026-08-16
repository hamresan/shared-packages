from sqlalchemy import select
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

    async def add(self, session: Session) -> None:
        self._session.add(self._mapper.to_model(session))

    async def save(self, session: Session) -> None:
        await self._session.merge(self._mapper.to_model(session))
