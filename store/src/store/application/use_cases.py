from typing import Protocol

from store.application.dto import (
    CreateStoreCommand,
    CreateStoreResult,
    GetOwnedStoreQuery,
    GetStoreQuery,
)
from store.domain import Store


class StoreCreator(Protocol):
    async def execute(self, command: CreateStoreCommand) -> CreateStoreResult: ...


class StoreReader(Protocol):
    async def execute(self, query: GetStoreQuery) -> Store | None: ...


class OwnedStoreReader(Protocol):
    async def execute(self, query: GetOwnedStoreQuery) -> Store | None: ...
