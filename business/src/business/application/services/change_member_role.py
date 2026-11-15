from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto_membership import ChangeMemberRoleCommand
from business.application.membership_access import MembershipManagementAccess
from business.application.membership_auditor import MembershipAuditor
from business.domain.enums import MembershipAuditAction, MembershipRole, MembershipStatus
from business.domain.errors import LastActiveOwnerError, MembershipNotFoundError
from business.domain.membership import BusinessMembership


class ChangeMemberRoleService:
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
        self, command: ChangeMemberRoleCommand, *, actor: AuthenticatedActor
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
            if (
                membership.role is MembershipRole.OWNER
                and membership.status is MembershipStatus.ACTIVE
                and command.role is MembershipRole.MEMBER
                and await uow.memberships.count_active_owners(command.business_id) <= 1
            ):
                raise LastActiveOwnerError("Cannot demote the last active owner")
            previous = membership.role.value
            membership.change_role(command.role, changed_at=self._clock.now())
            await uow.memberships.save(membership)
            await uow.membership_branch_access.replace(membership.id, ())
            await self._auditor.record(
                uow,
                membership,
                actor.user_id,
                MembershipAuditAction.ROLE_CHANGED,
                before=previous,
                after=membership.role.value,
            )
            await uow.commit()
            return membership
