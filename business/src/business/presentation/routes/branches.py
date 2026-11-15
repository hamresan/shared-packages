from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from business.application import AuthenticatedActor, ListBranchesQuery
from business.application.services import (
    ArchiveBranchService,
    CreateBranchService,
    GetBranchService,
    ListBranchesService,
    ReactivateBranchService,
    UpdateBranchService,
)
from business.presentation.dependencies.authentication import AuthenticatedActorDependency
from business.presentation.errors.http import BusinessHttpExecutor
from business.presentation.mappers import BranchRequestMapper, BranchResponseMapper
from business.presentation.schemas import BranchResponse, CreateBranchRequest, UpdateBranchRequest


class BranchRouterFactory:
    def __init__(
        self,
        auth: AuthenticatedActorDependency,
        creator: CreateBranchService,
        reader: GetBranchService,
        lister: ListBranchesService,
        updater: UpdateBranchService,
        archiver: ArchiveBranchService,
        reactivator: ReactivateBranchService,
        requests: BranchRequestMapper,
        responses: BranchResponseMapper,
        executor: BusinessHttpExecutor,
    ) -> None:
        self._auth, self._creator, self._reader, self._lister = auth, creator, reader, lister
        self._updater, self._archiver, self._reactivator = updater, archiver, reactivator
        self._requests, self._responses, self._executor = requests, responses, executor

    def create(self) -> APIRouter:
        auth = self._auth
        router = APIRouter(prefix="/businesses/{business_id}/branches", tags=["business-branches"])

        async def create_branch(
            business_id: UUID,
            request: CreateBranchRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> BranchResponse:
            result = await self._executor.run(
                self._creator.execute(self._requests.create(business_id, request), actor=actor)
            )
            return self._responses.to_response(result)

        async def list_branches(
            business_id: UUID,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
            city: str | None = None,
            country_code: str | None = None,
        ) -> list[BranchResponse]:
            result = await self._executor.run(
                self._lister.execute(
                    ListBranchesQuery(business_id, city=city, country_code=country_code),
                    actor=actor,
                )
            )
            return [self._responses.to_response(item) for item in result]

        async def get_branch(
            business_id: UUID, branch_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> BranchResponse:
            result = await self._executor.run(
                self._reader.execute(business_id, branch_id, actor=actor)
            )
            return self._responses.to_response(result)

        async def update_branch(
            business_id: UUID,
            branch_id: UUID,
            request: UpdateBranchRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> BranchResponse:
            result = await self._executor.run(
                self._updater.execute(
                    self._requests.update(business_id, branch_id, request), actor=actor
                )
            )
            return self._responses.to_response(result)

        async def archive_branch(
            business_id: UUID, branch_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> BranchResponse:
            result = await self._executor.run(
                self._archiver.execute(business_id, branch_id, actor=actor)
            )
            return self._responses.to_response(result)

        async def reactivate_branch(
            business_id: UUID, branch_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> BranchResponse:
            result = await self._executor.run(
                self._reactivator.execute(business_id, branch_id, actor=actor)
            )
            return self._responses.to_response(result)

        router.add_api_route(
            "",
            create_branch,
            methods=["POST"],
            response_model=BranchResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "", list_branches, methods=["GET"], response_model=list[BranchResponse]
        )
        router.add_api_route(
            "/{branch_id}", get_branch, methods=["GET"], response_model=BranchResponse
        )
        router.add_api_route(
            "/{branch_id}", update_branch, methods=["PUT"], response_model=BranchResponse
        )
        router.add_api_route(
            "/{branch_id}", archive_branch, methods=["DELETE"], response_model=BranchResponse
        )
        router.add_api_route(
            "/{branch_id}/reactivate",
            reactivate_branch,
            methods=["POST"],
            response_model=BranchResponse,
        )
        return router
