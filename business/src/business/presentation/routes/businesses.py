from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from business.application import AuthenticatedActor
from business.application.services import (
    ArchiveBusinessService,
    CreateBusinessService,
    GetBusinessService,
    ListBusinessesService,
    UpdateBusinessService,
)
from business.presentation.dependencies.authentication import AuthenticatedActorDependency
from business.presentation.errors.http import BusinessHttpExecutor
from business.presentation.mappers import BusinessRequestMapper, BusinessResponseMapper
from business.presentation.schemas import (
    BusinessResponse,
    CreateBusinessRequest,
    UpdateBusinessRequest,
)


class BusinessRouterFactory:
    def __init__(
        self,
        auth: AuthenticatedActorDependency,
        creator: CreateBusinessService,
        reader: GetBusinessService,
        lister: ListBusinessesService,
        updater: UpdateBusinessService,
        archiver: ArchiveBusinessService,
        requests: BusinessRequestMapper,
        responses: BusinessResponseMapper,
        executor: BusinessHttpExecutor,
    ) -> None:
        self._auth, self._creator, self._reader, self._lister = auth, creator, reader, lister
        self._updater, self._archiver = updater, archiver
        self._requests, self._responses, self._executor = requests, responses, executor

    def create(self) -> APIRouter:
        auth = self._auth
        router = APIRouter(prefix="/businesses", tags=["businesses"])

        async def create_business(
            request: CreateBusinessRequest, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> BusinessResponse:
            result = await self._executor.run(
                self._creator.execute(self._requests.create(request), actor=actor)
            )
            return self._responses.to_response(result)

        async def list_businesses(
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> list[BusinessResponse]:
            result = await self._executor.run(self._lister.execute(actor=actor))
            return [self._responses.to_response(item) for item in result]

        async def get_business(
            business_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> BusinessResponse:
            result = await self._executor.run(self._reader.execute(business_id, actor=actor))
            return self._responses.to_response(result)

        async def update_business(
            business_id: UUID,
            request: UpdateBusinessRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> BusinessResponse:
            result = await self._executor.run(
                self._updater.execute(self._requests.update(business_id, request), actor=actor)
            )
            return self._responses.to_response(result)

        async def archive_business(
            business_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> BusinessResponse:
            result = await self._executor.run(self._archiver.execute(business_id, actor=actor))
            return self._responses.to_response(result)

        router.add_api_route(
            "",
            create_business,
            methods=["POST"],
            response_model=BusinessResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "", list_businesses, methods=["GET"], response_model=list[BusinessResponse]
        )
        router.add_api_route(
            "/{business_id}", get_business, methods=["GET"], response_model=BusinessResponse
        )
        router.add_api_route(
            "/{business_id}", update_business, methods=["PUT"], response_model=BusinessResponse
        )
        router.add_api_route(
            "/{business_id}", archive_business, methods=["DELETE"], response_model=BusinessResponse
        )
        return router
