from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from store.presentation.dependencies import AuthenticatedActor, AuthenticatedActorDependency
from store.presentation.routes.endpoints import (
    CreateStoreEndpoint,
    GetOwnedStoreEndpoint,
    GetStoreEndpoint,
)
from store.presentation.schemas import CreateStoreRequest, StoreResponse


class StoreRouterFactory:
    def __init__(
        self,
        authenticated_actor_dependency: AuthenticatedActorDependency,
        create_store_endpoint: CreateStoreEndpoint,
        get_owned_store_endpoint: GetOwnedStoreEndpoint,
        get_store_endpoint: GetStoreEndpoint,
    ) -> None:
        self._authenticated_actor_dependency = authenticated_actor_dependency
        self._create_store_endpoint = create_store_endpoint
        self._get_owned_store_endpoint = get_owned_store_endpoint
        self._get_store_endpoint = get_store_endpoint

    def create(self) -> APIRouter:
        actor_dependency = self._authenticated_actor_dependency
        create_endpoint = self._create_store_endpoint
        get_owned_endpoint = self._get_owned_store_endpoint
        get_store_endpoint = self._get_store_endpoint

        router = APIRouter(prefix="/stores", tags=["stores"])

        async def create_store(
            request: CreateStoreRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> StoreResponse:
            return await create_endpoint(request, actor)

        async def get_owned_store(
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> StoreResponse:
            return await get_owned_endpoint(actor)

        async def get_store(
            store_id: UUID,
            _actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> StoreResponse:
            return await get_store_endpoint(store_id)

        router.add_api_route(
            "",
            create_store,
            methods=["POST"],
            response_model=StoreResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "/me",
            get_owned_store,
            methods=["GET"],
            response_model=StoreResponse,
        )
        router.add_api_route(
            "/{store_id}",
            get_store,
            methods=["GET"],
            response_model=StoreResponse,
        )
        return router
