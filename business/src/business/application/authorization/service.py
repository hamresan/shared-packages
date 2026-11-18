from uuid import UUID

from business.application.authorization.contracts import BusinessAuthorizationReader
from business.application.authorization.dto import MembershipAuthorizationInfo
from business.application.authorization.mapper import MembershipAuthorizationMapper
from business.application.contracts import BusinessUnitOfWorkFactory
from business.application.membership_access import MembershipBranchVisibility
from business.application.policies import BusinessAccessPolicy
from business.domain.enums import MembershipRole


class BusinessAuthorizationService(BusinessAuthorizationReader):
    """Read-only organization access queries for trusted host components."""

    def __init__(
        self,
        uow_factory: BusinessUnitOfWorkFactory,
        policy: BusinessAccessPolicy,
        visibility: MembershipBranchVisibility,
        mapper: MembershipAuthorizationMapper,
    ) -> None:
        self._uow_factory = uow_factory
        self._policy = policy
        self._visibility = visibility
        self._mapper = mapper

    async def get_membership(
        self, business_id: UUID, user_id: UUID
    ) -> MembershipAuthorizationInfo | None:
        async with self._uow_factory() as uow:
            if await uow.businesses.get_by_id(business_id) is None:
                return None
            membership = await uow.memberships.get_by_business_and_user(business_id, user_id)
            return self._mapper.to_info(membership) if membership is not None else None

    async def has_role(
        self, business_id: UUID, user_id: UUID, allowed_roles: frozenset[MembershipRole]
    ) -> bool:
        async with self._uow_factory() as uow:
            if await uow.businesses.get_by_id(business_id) is None:
                return False
            membership = await uow.memberships.get_by_business_and_user(business_id, user_id)
            return self._policy.has_any_role(membership, allowed_roles)

    async def can_access_branch(self, business_id: UUID, branch_id: UUID, user_id: UUID) -> bool:
        async with self._uow_factory() as uow:
            if await uow.businesses.get_by_id(business_id) is None:
                return False
            membership = await uow.memberships.get_by_business_and_user(business_id, user_id)
            if not self._policy.is_active_member(membership) or membership is None:
                return False
            branch = await uow.branches.get_for_business(business_id, branch_id)
            if branch is None:
                return False
            allowed = await self._visibility.allowed_ids(uow, membership)
            return allowed is None or branch_id in allowed
