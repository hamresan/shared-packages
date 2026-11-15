from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from copy import deepcopy
from uuid import UUID

from business.application.contracts import (
    BranchRepository,
    BusinessMembershipRepository,
    BusinessRepository,
    BusinessUnitOfWork,
    BusinessUnitOfWorkFactory,
    MembershipAuditRepository,
    MembershipBranchAccessRepository,
)
from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.membership import BusinessMembership
from business.domain.membership_audit import MembershipAuditRecord
from tests.support.fakes.branch_repository import InMemoryBranchRepository
from tests.support.fakes.business_repository import InMemoryBusinessRepository
from tests.support.fakes.database import InMemoryBusinessDatabase
from tests.support.fakes.membership_audit_repository import InMemoryMembershipAuditRepository
from tests.support.fakes.membership_branch_access_repository import (
    InMemoryMembershipBranchAccessRepository,
)
from tests.support.fakes.membership_repository import InMemoryBusinessMembershipRepository


class InMemoryBusinessUnitOfWork(BusinessUnitOfWork):
    def __init__(
        self,
        database: InMemoryBusinessDatabase,
        *,
        fail_membership_add: bool,
        fail_branch_add: bool,
        fail_commit: bool,
    ) -> None:
        self._database = database
        self._staged_businesses: dict[UUID, Business] = {}
        self._staged_memberships: dict[UUID, BusinessMembership] = {}
        self._staged_branches: dict[UUID, Branch] = {}
        self._staged_access: dict[UUID, tuple[UUID, ...]] = {}
        self._staged_audits: dict[UUID, MembershipAuditRecord] = {}
        self._businesses = InMemoryBusinessRepository(database, self._staged_businesses)
        self._memberships = InMemoryBusinessMembershipRepository(
            database, self._staged_memberships, fail_add=fail_membership_add
        )
        self._branches = InMemoryBranchRepository(
            database, self._staged_branches, fail_add=fail_branch_add
        )
        self._membership_branch_access = InMemoryMembershipBranchAccessRepository(
            database, self._staged_access
        )
        self._membership_audit = InMemoryMembershipAuditRepository(self._staged_audits)
        self._fail_commit = fail_commit

    @property
    def businesses(self) -> BusinessRepository:
        return self._businesses

    @property
    def memberships(self) -> BusinessMembershipRepository:
        return self._memberships

    @property
    def branches(self) -> BranchRepository:
        return self._branches

    @property
    def membership_branch_access(self) -> MembershipBranchAccessRepository:
        return self._membership_branch_access

    @property
    def membership_audit(self) -> MembershipAuditRepository:
        return self._membership_audit

    async def lock_business_membership(self, business_id: UUID) -> None:
        # The PostgreSQL adapter will acquire a transaction-scoped row lock in Stage 5.
        return None

    async def commit(self) -> None:
        if self._fail_commit:
            raise RuntimeError("Commit failed")
        self._database.businesses.update(deepcopy(self._staged_businesses))
        self._database.memberships.update(deepcopy(self._staged_memberships))
        self._database.branches.update(deepcopy(self._staged_branches))
        self._database.membership_branch_ids.update(self._staged_access)
        self._database.membership_audits.update(self._staged_audits)
        self._database.commit_count += 1
        self._staged_businesses.clear()
        self._staged_memberships.clear()
        self._staged_branches.clear()
        self._staged_access.clear()
        self._staged_audits.clear()


class InMemoryBusinessUnitOfWorkFactory(BusinessUnitOfWorkFactory):
    def __init__(
        self,
        database: InMemoryBusinessDatabase,
        *,
        fail_membership_add: bool = False,
        fail_branch_add: bool = False,
        fail_commit: bool = False,
    ) -> None:
        self._database = database
        self._fail_membership_add = fail_membership_add
        self._fail_branch_add = fail_branch_add
        self._fail_commit = fail_commit

    def __call__(self) -> AbstractAsyncContextManager[BusinessUnitOfWork]:
        return self._open()

    @asynccontextmanager
    async def _open(self) -> AsyncGenerator[BusinessUnitOfWork]:
        yield InMemoryBusinessUnitOfWork(
            self._database,
            fail_membership_add=self._fail_membership_add,
            fail_branch_add=self._fail_branch_add,
            fail_commit=self._fail_commit,
        )
