from uuid import UUID

from identity.application.contracts.database import AsyncSessionFactory
from identity.application.contracts.user_reader import UserReader
from identity.domain import User
from identity.infrastructure.persistence.sqlalchemy.mappers import UserMapper
from identity.infrastructure.persistence.sqlalchemy.models import UserModel
from sqlalchemy import select


class SqlAlchemyUserReader(UserReader):
    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        mapper: UserMapper | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._mapper = mapper or UserMapper()

    async def get_by_id(self, user_id: UUID) -> User | None:
        async with self._session_factory() as session:
            model = await session.scalar(select(UserModel).where(UserModel.id == user_id))
        return self._mapper.to_domain(model) if model is not None else None
