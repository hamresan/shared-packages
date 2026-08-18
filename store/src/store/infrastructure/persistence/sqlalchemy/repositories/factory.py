from sqlalchemy.ext.asyncio import AsyncSession

from store.application import StoreRepository
from store.infrastructure.persistence.sqlalchemy.mappers import StorePersistenceMapper
from store.infrastructure.persistence.sqlalchemy.repositories.store import SqlAlchemyStoreRepository


class SqlAlchemyStoreRepositoryFactory:
    def __init__(self, mapper: StorePersistenceMapper) -> None:
        self._mapper = mapper

    def create(self, session: AsyncSession) -> StoreRepository:
        return SqlAlchemyStoreRepository(session, self._mapper)
