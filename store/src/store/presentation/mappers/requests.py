from uuid import UUID

from store.application import CreateStoreCommand, GetOwnedStoreQuery, GetStoreQuery
from store.presentation.dependencies import AuthenticatedActor
from store.presentation.schemas import CreateStoreRequest


class StoreRequestMapper:
    def to_create_command(
        self,
        request: CreateStoreRequest,
        actor: AuthenticatedActor,
    ) -> CreateStoreCommand:
        return CreateStoreCommand(
            owner_user_id=actor.user_id,
            name=request.name,
            business_type=request.business_type,
            primary_language=request.primary_language,
            country_code=request.country_code,
            base_currency_code=request.base_currency_code,
        )

    def to_owned_store_query(self, actor: AuthenticatedActor) -> GetOwnedStoreQuery:
        return GetOwnedStoreQuery(owner_user_id=actor.user_id)

    def to_store_query(self, store_id: UUID) -> GetStoreQuery:
        return GetStoreQuery(store_id=store_id)
