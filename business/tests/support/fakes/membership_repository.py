from copy import deepcopy
from uuid import UUID

from business.application.contracts import BusinessMembershipRepository
from business.domain.membership import BusinessMembership
from tests.support.fakes.database import InMemoryBusinessDatabase


class InMemoryBusinessMembershipRepository(BusinessMembershipRepository):
    def __init__(
        self,
        database: InMemoryBusinessDatabase,
        staged_memberships: dict[UUID, BusinessMembership],
        *,
        fail_add: bool = False,
    ) -> None:
        self._database = database
        self._staged_memberships = staged_memberships
        self._fail_add = fail_add

    async def add(self, membership: BusinessMembership) -> None:
        if self._fail_add:
            raise RuntimeError("Membership write failed")
        self._staged_memberships[membership.id] = deepcopy(membership)

    async def get_by_business_and_user(
        self, business_id: UUID, user_id: UUID
    ) -> BusinessMembership | None:
        for membership in self._all_memberships():
            if membership.business_id == business_id and membership.user_id == user_id:
                return deepcopy(membership)
        return None

    async def list_by_user_id(self, user_id: UUID) -> tuple[BusinessMembership, ...]:
        return tuple(
            deepcopy(membership)
            for membership in self._all_memberships()
            if membership.user_id == user_id
        )

    def _all_memberships(self) -> tuple[BusinessMembership, ...]:
        combined = {**self._database.memberships, **self._staged_memberships}
        return tuple(combined.values())
