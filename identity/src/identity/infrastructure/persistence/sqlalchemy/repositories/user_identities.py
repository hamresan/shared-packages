from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from identity.application.contracts.repositories import UserIdentityRepository
from identity.domain import IdentityType, UserIdentity
from identity.infrastructure.persistence.sqlalchemy.mappers import UserIdentityMapper
from identity.infrastructure.persistence.sqlalchemy.models import UserIdentityModel


class SqlAlchemyUserIdentityRepository(UserIdentityRepository):
    def __init__(self, session: AsyncSession, mapper: UserIdentityMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get_by_destination(
        self,
        identity_type: IdentityType,
        normalized_value: str,
    ) -> UserIdentity | None:
        statement = select(UserIdentityModel).where(
            UserIdentityModel.type == identity_type,
            UserIdentityModel.normalized_value == normalized_value,
        )
        model = await self._session.scalar(statement)
        return self._mapper.to_domain(model) if model is not None else None

    async def add(self, identity: UserIdentity) -> None:
        self._session.add(self._mapper.to_model(identity))
