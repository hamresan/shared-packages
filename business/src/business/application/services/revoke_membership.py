from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.membership_access import MembershipManagementAccess
from business.application.membership_auditor import MembershipAuditor
from business.domain.enums import MembershipAuditAction, MembershipRole, MembershipStatus
from business.domain.errors import LastActiveOwnerError, MembershipNotFoundError
from business.domain.membership import BusinessMembership


class RevokeMembershipService:
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
        self, business_id: UUID, membership_id: UUID, *, actor: AuthenticatedActor
    ) -> BusinessMembership:
        async with self._uow_factory() as uow:
            await self._access.require_owner(uow, business_id, actor)
            await uow.lock_business_membership(business_id)
            await self._access.require_owner(uow, business_id, actor)
            membership = await uow.memberships.get_for_business(business_id, membership_id)
            if membership is None:
                raise MembershipNotFoundError("Membership was not found")
            if (
                membership.role is MembershipRole.OWNER
                and membership.status is MembershipStatus.ACTIVE
                and await uow.memberships.count_active_owners(business_id) <= 1
            ):
                raise LastActiveOwnerError("Cannot revoke the last active owner")
            membership.revoke(revoked_at=self._clock.now())
            await uow.memberships.save(membership)
            await uow.membership_branch_access.replace(membership.id, ())
            await self._auditor.record(
                uow, membership, actor.user_id, MembershipAuditAction.REVOKED
            )
            await uow.commit()
            return membership
