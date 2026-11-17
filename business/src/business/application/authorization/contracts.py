from typing import Protocol
from uuid import UUID

from business.application.authorization.dto import MembershipAuthorizationInfo
from business.domain.enums import MembershipRole


class BusinessAuthorizationReader(Protocol):
    async def get_membership(
        self, business_id: UUID, user_id: UUID
    ) -> MembershipAuthorizationInfo | None: ...

    async def has_role(
        self, business_id: UUID, user_id: UUID, allowed_roles: frozenset[MembershipRole]
    ) -> bool: ...

    async def can_access_branch(
        self, business_id: UUID, branch_id: UUID, user_id: UUID
    ) -> bool: ...
