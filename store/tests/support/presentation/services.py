from store.application import (
    CreateStoreCommand,
    CreateStoreResult,
    GetOwnedStoreQuery,
    GetStoreQuery,
    OwnedStoreReader,
    StoreCreator,
    StoreReader,
)
from store.domain import Store


class FakeStoreCreator(StoreCreator):
    def __init__(self, store: Store) -> None:
        self.store = store
        self.received_command: CreateStoreCommand | None = None
        self.error: ValueError | None = None

    async def execute(self, command: CreateStoreCommand) -> CreateStoreResult:
        self.received_command = command
        if self.error is not None:
            raise self.error
        self.store.owner_user_id = command.owner_user_id
        return CreateStoreResult(store=self.store)


class FakeOwnedStoreReader(OwnedStoreReader):
    def __init__(self, store: Store | None) -> None:
        self.store = store
        self.received_query: GetOwnedStoreQuery | None = None

    async def execute(self, query: GetOwnedStoreQuery) -> Store | None:
        self.received_query = query
        return self.store


class FakeStoreReader(StoreReader):
    def __init__(self, store: Store | None) -> None:
        self.store = store
        self.received_query: GetStoreQuery | None = None

    async def execute(self, query: GetStoreQuery) -> Store | None:
        self.received_query = query
        return self.store
