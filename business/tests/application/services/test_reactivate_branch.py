from datetime import UTC, datetime
from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.domain import (
    BranchAlreadyActiveError,
    BranchNotFoundError,
    BranchStatus,
    BusinessArchivedError,
    BusinessNotFoundError,
    BusinessStatus,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_TIME,
    TEST_USER_ID,
)
from tests.support.factories import build_reactivate_branch_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
)
from tests.support.scenarios import seed_branch, seed_owned_business


async def test_owner_reactivates_archived_branch_with_same_identity() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    branch = seed_branch(database, status=BranchStatus.ARCHIVED)
    reactivated_at = datetime(2026, 2, 1, tzinfo=UTC)

    restored = await build_reactivate_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(reactivated_at)
    ).execute(TEST_BUSINESS_ID, branch.id, actor=AuthenticatedActor(TEST_USER_ID))

    assert restored.id == TEST_BRANCH_ID
    assert restored.business_id == TEST_BUSINESS_ID
    assert restored.status is BranchStatus.ACTIVE
    assert restored.archived_at is None
    assert restored.updated_at == reactivated_at
    assert database.branches[branch.id].status is BranchStatus.ACTIVE
    assert database.commit_count == 1


async def test_active_branch_cannot_be_reactivated() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(BranchAlreadyActiveError):
        await build_reactivate_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID))

    assert database.commit_count == 0


async def test_unrelated_user_cannot_reactivate_archived_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database, status=BranchStatus.ARCHIVED)

    with pytest.raises(BusinessNotFoundError):
        await build_reactivate_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(OTHER_USER_ID))


async def test_owner_cannot_reactivate_foreign_business_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    foreign = seed_branch(database, business_id=UUID(int=91), status=BranchStatus.ARCHIVED)

    with pytest.raises(BranchNotFoundError):
        await build_reactivate_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, foreign.id, actor=AuthenticatedActor(TEST_USER_ID))


async def test_archived_business_cannot_reactivate_its_branches() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database, status=BusinessStatus.ARCHIVED)
    seed_branch(database, status=BranchStatus.ARCHIVED)

    with pytest.raises(BusinessArchivedError):
        await build_reactivate_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID))


async def test_reactivate_commit_failure_preserves_archived_status() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database, status=BranchStatus.ARCHIVED)

    with pytest.raises(RuntimeError, match="Commit failed"):
        await build_reactivate_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database, fail_commit=True), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID))

    assert database.branches[TEST_BRANCH_ID].status is BranchStatus.ARCHIVED
    assert database.commit_count == 0
