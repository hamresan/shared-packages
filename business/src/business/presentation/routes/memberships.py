from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from business.application import AuthenticatedActor
from business.application.services import (
    AcceptMembershipService,
    ChangeMemberRoleService,
    InviteMemberService,
    ListMembershipsService,
    RevokeMembershipService,
    SetMemberBranchAccessService,
    TransferOwnershipService,
)
from business.presentation.dependencies.authentication import AuthenticatedActorDependency
from business.presentation.errors.http import BusinessHttpExecutor
from business.presentation.mappers import MembershipRequestMapper, MembershipResponseMapper
from business.presentation.schemas import (
    ChangeMemberRoleRequest,
    InviteMemberRequest,
    MembershipResponse,
    SetMemberBranchAccessRequest,
    TransferOwnershipRequest,
)


class MembershipRouterFactory:
    def __init__(
        self,
        auth: AuthenticatedActorDependency,
        inviter: InviteMemberService,
        accepter: AcceptMembershipService,
        lister: ListMembershipsService,
        role_changer: ChangeMemberRoleService,
        revoker: RevokeMembershipService,
        access_setter: SetMemberBranchAccessService,
        transfer: TransferOwnershipService,
        requests: MembershipRequestMapper,
        responses: MembershipResponseMapper,
        executor: BusinessHttpExecutor,
    ) -> None:
        self._auth = auth
        self._inviter, self._accepter, self._lister = inviter, accepter, lister
        self._role_changer, self._revoker = role_changer, revoker
        self._access_setter, self._transfer = access_setter, transfer
        self._requests, self._responses, self._executor = requests, responses, executor

    def create(self) -> APIRouter:
        auth = self._auth
        router = APIRouter(prefix="/businesses/{business_id}", tags=["business-memberships"])

        async def invite_member(
            business_id: UUID,
            request: InviteMemberRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> MembershipResponse:
            result = await self._executor.run(
                self._inviter.execute(self._requests.invite(business_id, request), actor=actor)
            )
            return self._responses.to_response(result)

        async def accept_member(
            business_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> MembershipResponse:
            result = await self._executor.run(self._accepter.execute(business_id, actor=actor))
            return self._responses.to_response(result)

        async def list_members(
            business_id: UUID, actor: Annotated[AuthenticatedActor, Depends(auth)]
        ) -> list[MembershipResponse]:
            result = await self._executor.run(self._lister.execute(business_id, actor=actor))
            return [self._responses.to_response(item) for item in result]

        async def change_role(
            business_id: UUID,
            membership_id: UUID,
            request: ChangeMemberRoleRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> MembershipResponse:
            result = await self._executor.run(
                self._role_changer.execute(
                    self._requests.change_role(business_id, membership_id, request), actor=actor
                )
            )
            return self._responses.to_response(result)

        async def revoke_member(
            business_id: UUID,
            membership_id: UUID,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> MembershipResponse:
            result = await self._executor.run(
                self._revoker.execute(business_id, membership_id, actor=actor)
            )
            return self._responses.to_response(result)

        async def set_access(
            business_id: UUID,
            membership_id: UUID,
            request: SetMemberBranchAccessRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> MembershipResponse:
            result = await self._executor.run(
                self._access_setter.execute(
                    self._requests.set_branch_access(business_id, membership_id, request),
                    actor=actor,
                )
            )
            return self._responses.to_response(result)

        async def transfer_ownership(
            business_id: UUID,
            request: TransferOwnershipRequest,
            actor: Annotated[AuthenticatedActor, Depends(auth)],
        ) -> MembershipResponse:
            result = await self._executor.run(
                self._transfer.execute(self._requests.transfer(business_id, request), actor=actor)
            )
            return self._responses.to_response(result)

        router.add_api_route(
            "/memberships",
            invite_member,
            methods=["POST"],
            response_model=MembershipResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "/memberships", list_members, methods=["GET"], response_model=list[MembershipResponse]
        )
        router.add_api_route(
            "/memberships/accept",
            accept_member,
            methods=["POST"],
            response_model=MembershipResponse,
        )
        router.add_api_route(
            "/memberships/{membership_id}/role",
            change_role,
            methods=["PUT"],
            response_model=MembershipResponse,
        )
        router.add_api_route(
            "/memberships/{membership_id}/access",
            set_access,
            methods=["PUT"],
            response_model=MembershipResponse,
        )
        router.add_api_route(
            "/memberships/{membership_id}",
            revoke_member,
            methods=["DELETE"],
            response_model=MembershipResponse,
        )
        router.add_api_route(
            "/ownership/transfer",
            transfer_ownership,
            methods=["POST"],
            response_model=MembershipResponse,
        )
        return router
