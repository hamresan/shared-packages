from dataclasses import dataclass

from business.application.services import (
    AcceptMembershipService,
    ArchiveBranchService,
    ArchiveBusinessService,
    ChangeMemberRoleService,
    CreateBranchService,
    CreateBusinessService,
    GetBranchService,
    GetBusinessService,
    InviteMemberService,
    ListBranchesService,
    ListBusinessesService,
    ListMembershipsService,
    ReactivateBranchService,
    RevokeMembershipService,
    SetMemberBranchAccessService,
    TransferOwnershipService,
    UpdateBranchService,
    UpdateBusinessService,
)


@dataclass(frozen=True, slots=True)
class BusinessUseCases:
    create: CreateBusinessService
    get: GetBusinessService
    list: ListBusinessesService
    update: UpdateBusinessService
    archive: ArchiveBusinessService


@dataclass(frozen=True, slots=True)
class BranchUseCases:
    create: CreateBranchService
    get: GetBranchService
    list: ListBranchesService
    update: UpdateBranchService
    archive: ArchiveBranchService
    reactivate: ReactivateBranchService


@dataclass(frozen=True, slots=True)
class MembershipUseCases:
    invite: InviteMemberService
    accept: AcceptMembershipService
    list: ListMembershipsService
    change_role: ChangeMemberRoleService
    revoke: RevokeMembershipService
    set_access: SetMemberBranchAccessService
    transfer: TransferOwnershipService
