from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from store.application import StoreRepository, StoreUnitOfWork
from store.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyStoreRepositoryFactory,
)
from store.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory


class SqlAlchemyStoreUnitOfWork(StoreUnitOfWork):
    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        repository_factory: SqlAlchemyStoreRepositoryFactory,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factory = repository_factory
        self._session_context: AbstractAsyncContextManager[AsyncSession] | None = None
        self._session: AsyncSession | None = None
        self._stores: StoreRepository | None = None

    @property
    def stores(self) -> StoreRepository:
        if self._stores is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._stores

    async def __aenter__(self) -> Self:
        self._session_context = self._session_factory()
        self._session = await self._session_context.__aenter__()
        self._stores = self._repository_factory.create(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is not None and exc is not None:
            await self._session.rollback()
        if self._session_context is not None:
            await self._session_context.__aexit__(exc_type, exc, traceback)

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        await self._session.commit()


class SqlAlchemyStoreUnitOfWorkFactory:
    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        repository_factory: SqlAlchemyStoreRepositoryFactory,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factory = repository_factory

    def __call__(self) -> SqlAlchemyStoreUnitOfWork:
        return SqlAlchemyStoreUnitOfWork(self._session_factory, self._repository_factory)
