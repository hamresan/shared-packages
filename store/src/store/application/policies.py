from store.application.contracts import StoreRepository


class StoreOwnershipPolicy:
    async def ensure_owner_can_create(
        self,
        repository: StoreRepository,
        owner_user_id,
    ) -> None:
        existing = await repository.get_by_owner_id(owner_user_id)
        if existing is not None:
            raise ValueError("Owner already has a store")
