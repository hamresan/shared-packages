from store.application.contracts import StoreUnitOfWorkFactory
from store.application.dto import (
    CreateStoreCommand,
    CreateStoreResult,
    GetOwnedStoreQuery,
    GetStoreQuery,
)
from store.application.factory import StoreFactory
from store.application.policies import StoreOwnershipPolicy
from store.application.validators import CreateStoreCommandValidator
from store.domain import Store


class CreateStoreService:
    def __init__(
        self,
        unit_of_work_factory: StoreUnitOfWorkFactory,
        validator: CreateStoreCommandValidator,
        ownership_policy: StoreOwnershipPolicy,
        factory: StoreFactory,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._validator = validator
        self._ownership_policy = ownership_policy
        self._factory = factory

    async def execute(self, command: CreateStoreCommand) -> CreateStoreResult:
        validated = self._validator.validate(command)
        async with self._unit_of_work_factory() as unit_of_work:
            await self._ownership_policy.ensure_owner_can_create(
                unit_of_work.stores,
                validated.owner_user_id,
            )
            store = self._factory.create(validated)
            await unit_of_work.stores.add(store)
            await unit_of_work.commit()
        return CreateStoreResult(store=store)


class GetStoreService:
    def __init__(self, unit_of_work_factory: StoreUnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    async def execute(self, query: GetStoreQuery) -> Store | None:
        async with self._unit_of_work_factory() as unit_of_work:
            return await unit_of_work.stores.get_by_id(query.store_id)


class GetOwnedStoreService:
    def __init__(self, unit_of_work_factory: StoreUnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    async def execute(self, query: GetOwnedStoreQuery) -> Store | None:
        async with self._unit_of_work_factory() as unit_of_work:
            return await unit_of_work.stores.get_by_owner_id(query.owner_user_id)
