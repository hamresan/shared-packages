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
)
from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.membership import BusinessMembership
from tests.support.fakes.branch_repository import InMemoryBranchRepository
from tests.support.fakes.business_repository import InMemoryBusinessRepository
from tests.support.fakes.database import InMemoryBusinessDatabase
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
        self._businesses = InMemoryBusinessRepository(database, self._staged_businesses)
        self._memberships = InMemoryBusinessMembershipRepository(
            database, self._staged_memberships, fail_add=fail_membership_add
        )
        self._branches = InMemoryBranchRepository(
            database, self._staged_branches, fail_add=fail_branch_add
        )
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

    async def commit(self) -> None:
        if self._fail_commit:
            raise RuntimeError("Commit failed")
        self._database.businesses.update(deepcopy(self._staged_businesses))
        self._database.memberships.update(deepcopy(self._staged_memberships))
        self._database.branches.update(deepcopy(self._staged_branches))
        self._database.commit_count += 1
        self._staged_businesses.clear()
        self._staged_memberships.clear()
        self._staged_branches.clear()


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
