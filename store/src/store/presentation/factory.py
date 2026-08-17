from store.application import OwnedStoreReader, StoreCreator, StoreReader
from store.presentation.dependencies import AuthenticatedActorDependency
from store.presentation.errors import StoreHttpErrorMapper
from store.presentation.fastapi import FastApiStoreAdapter
from store.presentation.mappers import (
    StoreRequestMapper,
    StoreResponseMapper,
    StoreValueObjectResponseMapper,
)
from store.presentation.routes import (
    CreateStoreEndpoint,
    GetOwnedStoreEndpoint,
    GetStoreEndpoint,
    StoreRouterFactory,
)


def build_fastapi_store_adapter(
    *,
    authenticated_actor_dependency: AuthenticatedActorDependency,
    store_creator: StoreCreator,
    owned_store_reader: OwnedStoreReader,
    store_reader: StoreReader,
) -> FastApiStoreAdapter:
    request_mapper = StoreRequestMapper()
    response_mapper = StoreResponseMapper(StoreValueObjectResponseMapper())
    error_mapper = StoreHttpErrorMapper()
    router_factory = StoreRouterFactory(
        authenticated_actor_dependency=authenticated_actor_dependency,
        create_store_endpoint=CreateStoreEndpoint(
            store_creator,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
        get_owned_store_endpoint=GetOwnedStoreEndpoint(
            owned_store_reader,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
        get_store_endpoint=GetStoreEndpoint(
            store_reader,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
    )
    return FastApiStoreAdapter(store_router=router_factory.create())
