from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto_membership import SetMemberBranchAccessCommand
from business.application.membership_access import MembershipManagementAccess
from business.application.membership_auditor import MembershipAuditor
from business.domain.enums import (
    BranchAccessScope,
    MembershipAuditAction,
    MembershipRole,
    MembershipStatus,
)
from business.domain.errors import (
    BranchNotFoundError,
    MembershipInvalidStateError,
    MembershipNotFoundError,
)
from business.domain.membership import BusinessMembership


class SetMemberBranchAccessService:
    def __init__(
        self,
        uow_factory: BusinessUnitOfWorkFactory,
        access: MembershipManagementAccess,
        clock: Clock,
        auditor: MembershipAuditor,
    ) -> None:
        self._uow_factory = uow_factory
        self._access = access
        self._clock = clock
        self._auditor = auditor

    async def execute(
        self, command: SetMemberBranchAccessCommand, *, actor: AuthenticatedActor
    ) -> BusinessMembership:
        async with self._uow_factory() as uow:
            await self._access.require_owner(uow, command.business_id, actor)
            await uow.lock_business_membership(command.business_id)
            await self._access.require_owner(uow, command.business_id, actor)
            membership = await uow.memberships.get_for_business(
                command.business_id, command.membership_id
            )
            if membership is None:
                raise MembershipNotFoundError("Membership was not found")
            if membership.status is MembershipStatus.REVOKED:
                raise MembershipInvalidStateError("Revoked membership cannot change access")
            if (
                membership.role in (MembershipRole.OWNER, MembershipRole.MANAGER)
                and command.scope is not BranchAccessScope.ALL
            ):
                raise MembershipInvalidStateError(
                    "Owners and managers must have full branch access"
                )
            if command.scope is BranchAccessScope.ALL and command.branch_ids:
                raise MembershipInvalidStateError("ALL scope cannot specify selected branch IDs")
            branch_ids = (
                tuple(dict.fromkeys(command.branch_ids))
                if command.scope is BranchAccessScope.SELECTED
                else ()
            )
            for branch_id in branch_ids:
                if await uow.branches.get_for_business(command.business_id, branch_id) is None:
                    raise BranchNotFoundError("Branch does not belong to this business")
            previous = membership.branch_access_scope.value
            membership.change_branch_scope(command.scope, changed_at=self._clock.now())
            await uow.memberships.save(membership)
            await uow.membership_branch_access.replace(membership.id, branch_ids)
            await self._auditor.record(
                uow,
                membership,
                actor.user_id,
                MembershipAuditAction.BRANCH_ACCESS_CHANGED,
                before=previous,
                after=command.scope.value,
                branch_ids=branch_ids,
            )
            await uow.commit()
            return membership
