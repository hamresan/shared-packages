from uuid import UUID

from business.application.contracts import MembershipBranchAccessRepository
from tests.support.fakes.database import InMemoryBusinessDatabase


class InMemoryMembershipBranchAccessRepository(MembershipBranchAccessRepository):
    def __init__(
        self, database: InMemoryBusinessDatabase, staged: dict[UUID, tuple[UUID, ...]]
    ) -> None:
        self._database = database
        self._staged = staged

    async def list_branch_ids(self, membership_id: UUID) -> tuple[UUID, ...]:
        return self._staged.get(
            membership_id, self._database.membership_branch_ids.get(membership_id, ())
        )

    async def replace(self, membership_id: UUID, branch_ids: tuple[UUID, ...]) -> None:
        self._staged[membership_id] = branch_ids
