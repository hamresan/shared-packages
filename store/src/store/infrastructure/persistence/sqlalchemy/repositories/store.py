from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from store.application import StoreRepository
from store.domain import Store
from store.infrastructure.persistence.sqlalchemy.mappers import StorePersistenceMapper
from store.infrastructure.persistence.sqlalchemy.models import StoreModel


class SqlAlchemyStoreRepository(StoreRepository):
    def __init__(self, session: AsyncSession, mapper: StorePersistenceMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def add(self, store: Store) -> None:
        self._session.add(self._mapper.to_model(store))

    async def get_by_id(self, store_id: UUID) -> Store | None:
        model = await self._session.scalar(select(StoreModel).where(StoreModel.id == store_id))
        return self._mapper.to_domain(model) if model is not None else None

    async def get_by_owner_id(self, owner_user_id: UUID) -> Store | None:
        model = await self._session.scalar(
            select(StoreModel).where(StoreModel.owner_user_id == owner_user_id)
        )
        return self._mapper.to_domain(model) if model is not None else None
