from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Protocol
from uuid import UUID

from store.domain import Store


class StoreRepository(Protocol):
    async def add(self, store: Store) -> None: ...

    async def get_by_id(self, store_id: UUID) -> Store | None: ...

    async def get_by_owner_id(self, owner_user_id: UUID) -> Store | None: ...


class StoreUnitOfWork(Protocol):
    @property
    def stores(self) -> StoreRepository: ...

    async def commit(self) -> None: ...


class StoreUnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[StoreUnitOfWork]: ...


class StoreIdentifierGenerator(Protocol):
    def new_store_id(self) -> UUID: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
