from uuid import UUID

from business.application.contracts import BusinessUnitOfWork, Clock, IdentifierGenerator
from business.domain.enums import MembershipAuditAction
from business.domain.membership import BusinessMembership
from business.domain.membership_audit import MembershipAuditRecord


class MembershipAuditor:
    def __init__(self, clock: Clock, ids: IdentifierGenerator) -> None:
        self._clock = clock
        self._ids = ids

    async def record(
        self,
        uow: BusinessUnitOfWork,
        membership: BusinessMembership,
        actor_id: UUID,
        action: MembershipAuditAction,
        *,
        before: str | None = None,
        after: str | None = None,
        branch_ids: tuple[UUID, ...] = (),
    ) -> None:
        await uow.membership_audit.add(
            MembershipAuditRecord(
                id=self._ids.new_id(),
                business_id=membership.business_id,
                membership_id=membership.id,
                actor_user_id=actor_id,
                action=action,
                occurred_at=self._clock.now(),
                previous_value=before,
                new_value=after,
                branch_ids=branch_ids,
            )
        )
