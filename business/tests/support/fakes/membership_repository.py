from copy import deepcopy
from uuid import UUID

from business.application.contracts import BusinessMembershipRepository
from business.domain.enums import MembershipRole, MembershipStatus
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
        matches = [
            membership
            for membership in self._all_memberships()
            if membership.business_id == business_id and membership.user_id == user_id
        ]
        current = next(
            (
                membership
                for membership in reversed(matches)
                if membership.status is not MembershipStatus.REVOKED
            ),
            None,
        )
        return deepcopy(current) if current is not None else None

    async def list_by_user_id(self, user_id: UUID) -> tuple[BusinessMembership, ...]:
        return tuple(
            deepcopy(membership)
            for membership in self._all_memberships()
            if membership.user_id == user_id and membership.status is MembershipStatus.ACTIVE
        )

    async def get_for_business(
        self, business_id: UUID, membership_id: UUID
    ) -> BusinessMembership | None:
        membership = next(
            (
                item
                for item in self._all_memberships()
                if item.id == membership_id and item.business_id == business_id
            ),
            None,
        )
        return deepcopy(membership) if membership is not None else None

    async def list_for_business(self, business_id: UUID) -> tuple[BusinessMembership, ...]:
        return tuple(
            deepcopy(item) for item in self._all_memberships() if item.business_id == business_id
        )

    async def count_active_owners(self, business_id: UUID) -> int:
        return sum(
            item.business_id == business_id
            and item.status is MembershipStatus.ACTIVE
            and item.role is MembershipRole.OWNER
            for item in self._all_memberships()
        )

    async def save(self, membership: BusinessMembership) -> None:
        self._staged_memberships[membership.id] = deepcopy(membership)

    def _all_memberships(self) -> tuple[BusinessMembership, ...]:
        combined = {**self._database.memberships, **self._staged_memberships}
        return tuple(combined.values())
