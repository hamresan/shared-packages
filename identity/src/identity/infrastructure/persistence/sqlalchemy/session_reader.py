from uuid import UUID

from sqlalchemy import select

from identity.application.contracts.database import AsyncSessionFactory
from identity.application.contracts.session_reader import SessionReader
from identity.domain import Session
from identity.infrastructure.persistence.sqlalchemy.mappers import SessionMapper
from identity.infrastructure.persistence.sqlalchemy.models import SessionModel


class SqlAlchemySessionReader(SessionReader):
    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        mapper: SessionMapper | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._mapper = mapper or SessionMapper()

    async def get_by_id(self, session_id: UUID) -> Session | None:
        async with self._session_factory() as session:
            model = await session.scalar(
                select(SessionModel).where(SessionModel.id == session_id)
            )
        return self._mapper.to_domain(model) if model is not None else None
