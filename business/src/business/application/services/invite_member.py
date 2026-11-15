from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock, IdentifierGenerator
from business.application.dto_membership import InviteMemberCommand
from business.application.membership_access import MembershipManagementAccess
from business.application.membership_auditor import MembershipAuditor
from business.domain.enums import (
    BranchAccessScope,
    MembershipAuditAction,
    MembershipRole,
    MembershipStatus,
)
from business.domain.errors import MembershipAlreadyExistsError
from business.domain.membership import BusinessMembership


class InviteMemberService:
    def __init__(
        self,
        uow_factory: BusinessUnitOfWorkFactory,
        access: MembershipManagementAccess,
        clock: Clock,
        ids: IdentifierGenerator,
        auditor: MembershipAuditor,
    ) -> None:
        self._uow_factory = uow_factory
        self._access = access
        self._clock = clock
        self._ids = ids
        self._auditor = auditor

    async def execute(
        self, command: InviteMemberCommand, *, actor: AuthenticatedActor
    ) -> BusinessMembership:
        async with self._uow_factory() as uow:
            await self._access.require_owner(uow, command.business_id, actor)
            await uow.lock_business_membership(command.business_id)
            await self._access.require_owner(uow, command.business_id, actor)
            existing = await uow.memberships.get_by_business_and_user(
                command.business_id, command.user_id
            )
            if existing is not None:
                raise MembershipAlreadyExistsError("User already has a membership or invitation")
            now = self._clock.now()
            membership = BusinessMembership(
                id=self._ids.new_id(),
                business_id=command.business_id,
                user_id=command.user_id,
                role=MembershipRole.MEMBER,
                status=MembershipStatus.INVITED,
                created_at=now,
                updated_at=now,
                branch_access_scope=BranchAccessScope.SELECTED,
            )
            await uow.memberships.add(membership)
            await self._auditor.record(
                uow, membership, actor.user_id, MembershipAuditAction.INVITED
            )
            await uow.commit()
            return membership
