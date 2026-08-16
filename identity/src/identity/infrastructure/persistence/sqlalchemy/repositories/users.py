from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from identity.application.contracts.repositories import UserRepository
from identity.domain import User
from identity.infrastructure.persistence.sqlalchemy.mappers import UserMapper
from identity.infrastructure.persistence.sqlalchemy.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession, mapper: UserMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._mapper.to_domain(model) if model is not None else None

    async def add(self, user: User) -> None:
        self._session.add(self._mapper.to_model(user))
