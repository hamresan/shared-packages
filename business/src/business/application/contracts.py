from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Protocol
from uuid import UUID

from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.membership import BusinessMembership
from business.domain.membership_audit import MembershipAuditRecord


class BusinessRepository(Protocol):
    async def add(self, business: Business) -> None: ...

    async def get_by_id(self, business_id: UUID) -> Business | None: ...

    async def list_by_ids(self, business_ids: tuple[UUID, ...]) -> tuple[Business, ...]: ...

    async def save(self, business: Business) -> None: ...


class BusinessMembershipRepository(Protocol):
    async def add(self, membership: BusinessMembership) -> None: ...

    async def get_by_business_and_user(
        self, business_id: UUID, user_id: UUID
    ) -> BusinessMembership | None: ...

    async def list_by_user_id(self, user_id: UUID) -> tuple[BusinessMembership, ...]: ...

    async def get_for_business(
        self, business_id: UUID, membership_id: UUID
    ) -> BusinessMembership | None: ...

    async def list_for_business(self, business_id: UUID) -> tuple[BusinessMembership, ...]: ...

    async def count_active_owners(self, business_id: UUID) -> int: ...

    async def save(self, membership: BusinessMembership) -> None: ...


class MembershipBranchAccessRepository(Protocol):
    async def list_branch_ids(self, membership_id: UUID) -> tuple[UUID, ...]: ...

    async def replace(self, membership_id: UUID, branch_ids: tuple[UUID, ...]) -> None: ...


class MembershipAuditRepository(Protocol):
    async def add(self, record: MembershipAuditRecord) -> None: ...


class BranchRepository(Protocol):
    async def add(self, branch: Branch) -> None: ...

    async def get_for_business(self, business_id: UUID, branch_id: UUID) -> Branch | None: ...

    async def list_for_business(
        self,
        business_id: UUID,
        *,
        city: str | None,
        country_code: str | None,
        allowed_branch_ids: tuple[UUID, ...] | None = None,
    ) -> tuple[Branch, ...]: ...

    async def save(self, branch: Branch) -> None: ...


class BusinessUnitOfWork(Protocol):
    @property
    def businesses(self) -> BusinessRepository: ...

    @property
    def memberships(self) -> BusinessMembershipRepository: ...

    @property
    def branches(self) -> BranchRepository: ...

    @property
    def membership_branch_access(self) -> MembershipBranchAccessRepository: ...

    @property
    def membership_audit(self) -> MembershipAuditRepository: ...

    async def lock_business_membership(self, business_id: UUID) -> None: ...

    async def commit(self) -> None: ...


class BusinessUnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[BusinessUnitOfWork]: ...


class IdentifierGenerator(Protocol):
    def new_id(self) -> UUID: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
