from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.membership_auditor import MembershipAuditor
from business.domain.enums import MembershipAuditAction
from business.domain.errors import MembershipNotFoundError
from business.domain.membership import BusinessMembership


class AcceptMembershipService:
    def __init__(
        self, uow_factory: BusinessUnitOfWorkFactory, clock: Clock, auditor: MembershipAuditor
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._auditor = auditor

    async def execute(self, business_id: UUID, *, actor: AuthenticatedActor) -> BusinessMembership:
        async with self._uow_factory() as uow:
            await uow.lock_business_membership(business_id)
            membership = await uow.memberships.get_by_business_and_user(business_id, actor.user_id)
            if membership is None:
                raise MembershipNotFoundError("Invitation was not found")
            membership.accept(accepted_at=self._clock.now())
            await uow.memberships.save(membership)
            await self._auditor.record(
                uow, membership, actor.user_id, MembershipAuditAction.ACCEPTED
            )
            await uow.commit()
            return membership
