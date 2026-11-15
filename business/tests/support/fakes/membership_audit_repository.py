from uuid import UUID

from business.application.contracts import MembershipAuditRepository
from business.domain.membership_audit import MembershipAuditRecord


class InMemoryMembershipAuditRepository(MembershipAuditRepository):
    def __init__(self, staged: dict[UUID, MembershipAuditRecord]) -> None:
        self._staged = staged

    async def add(self, record: MembershipAuditRecord) -> None:
        self._staged[record.id] = record
