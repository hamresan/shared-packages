from uuid import UUID

from business.application.dto import (
    CreateBranchCommand,
    CreateBusinessCommand,
    UpdateBranchCommand,
    UpdateBusinessCommand,
)
from business.application.dto_membership import (
    ChangeMemberRoleCommand,
    InviteMemberCommand,
    SetMemberBranchAccessCommand,
    TransferOwnershipCommand,
)
from business.domain.value_objects import BranchAddress, BranchContact
from business.presentation.schemas import (
    ChangeMemberRoleRequest,
    CreateBranchRequest,
    CreateBusinessRequest,
    InviteMemberRequest,
    SetMemberBranchAccessRequest,
    TransferOwnershipRequest,
    UpdateBranchRequest,
    UpdateBusinessRequest,
)
from business.presentation.schemas.branch import BranchAddressSchema, BranchContactSchema


class BusinessRequestMapper:
    def create(self, request: CreateBusinessRequest) -> CreateBusinessCommand:
        return CreateBusinessCommand(**request.model_dump())

    def update(self, business_id: UUID, request: UpdateBusinessRequest) -> UpdateBusinessCommand:
        return UpdateBusinessCommand(business_id=business_id, **request.model_dump())


class BranchRequestMapper:
    def create(self, business_id: UUID, request: CreateBranchRequest) -> CreateBranchCommand:
        return CreateBranchCommand(
            business_id=business_id,
            name=request.name,
            timezone=request.timezone,
            address=self._address(request.address),
            contact=self._contact(request.contact),
        )

    def update(
        self, business_id: UUID, branch_id: UUID, request: UpdateBranchRequest
    ) -> UpdateBranchCommand:
        return UpdateBranchCommand(
            business_id=business_id,
            branch_id=branch_id,
            name=request.name,
            timezone=request.timezone,
            address=self._address(request.address),
            contact=self._contact(request.contact),
        )

    def _address(self, request: BranchAddressSchema | None) -> BranchAddress | None:
        return BranchAddress(**request.model_dump()) if request is not None else None

    def _contact(self, request: BranchContactSchema | None) -> BranchContact | None:
        return BranchContact(**request.model_dump()) if request is not None else None


class MembershipRequestMapper:
    def invite(self, business_id: UUID, request: InviteMemberRequest) -> InviteMemberCommand:
        return InviteMemberCommand(business_id, request.user_id)

    def change_role(
        self, business_id: UUID, membership_id: UUID, request: ChangeMemberRoleRequest
    ) -> ChangeMemberRoleCommand:
        return ChangeMemberRoleCommand(business_id, membership_id, request.role)

    def set_branch_access(
        self, business_id: UUID, membership_id: UUID, request: SetMemberBranchAccessRequest
    ) -> SetMemberBranchAccessCommand:
        return SetMemberBranchAccessCommand(
            business_id, membership_id, request.scope, request.branch_ids
        )

    def transfer(
        self, business_id: UUID, request: TransferOwnershipRequest
    ) -> TransferOwnershipCommand:
        return TransferOwnershipCommand(business_id, request.recipient_membership_id)
