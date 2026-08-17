from contextlib import AbstractAsyncContextManager
from datetime import UTC, datetime
from types import TracebackType
from uuid import UUID

from store.application import StoreRepository, StoreUnitOfWork
from store.domain import Store


class FakeStoreRepository(StoreRepository):
    def __init__(self, stores: list[Store] | None = None) -> None:
        self._stores = list(stores or [])
        self.added: list[Store] = []

    async def add(self, store: Store) -> None:
        self._stores.append(store)
        self.added.append(store)

    async def get_by_id(self, store_id: UUID) -> Store | None:
        return next((store for store in self._stores if store.id == store_id), None)

    async def get_by_owner_id(self, owner_user_id: UUID) -> Store | None:
        return next(
            (store for store in self._stores if store.owner_user_id == owner_user_id),
            None,
        )


class FakeStoreUnitOfWork(StoreUnitOfWork):
    def __init__(self, repository: FakeStoreRepository) -> None:
        self._repository = repository
        self.committed = False

    @property
    def stores(self) -> StoreRepository:
        return self._repository

    async def commit(self) -> None:
        self.committed = True


class FakeStoreUnitOfWorkContext(AbstractAsyncContextManager[StoreUnitOfWork]):
    def __init__(self, unit_of_work: FakeStoreUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def __aenter__(self) -> StoreUnitOfWork:
        return self._unit_of_work

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return None


class FakeStoreUnitOfWorkFactory:
    def __init__(self, unit_of_work: FakeStoreUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def __call__(self) -> AbstractAsyncContextManager[StoreUnitOfWork]:
        return FakeStoreUnitOfWorkContext(self._unit_of_work)


class FixedClock:
    def __init__(self, value: datetime | None = None) -> None:
        self._value = value or datetime(2026, 8, 17, 8, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self._value


class FixedStoreIdentifierGenerator:
    def __init__(self, store_id: UUID) -> None:
        self._store_id = store_id

    def new_store_id(self) -> UUID:
        return self._store_id
