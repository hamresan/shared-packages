from datetime import UTC, datetime
from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.domain import (
    BranchArchivedError,
    BranchNotFoundError,
    BranchStatus,
    BusinessArchivedError,
    BusinessPermissionDeniedError,
    BusinessStatus,
    MembershipRole,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_TIME,
    TEST_USER_ID,
    build_membership,
)
from tests.support.factories import build_archive_branch_service, build_get_branch_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
)
from tests.support.scenarios import seed_branch, seed_owned_business


async def test_owner_archives_branch_without_deleting_it_or_business() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    second = seed_branch(database, branch_id=UUID(int=10))
    uow_factory = InMemoryBusinessUnitOfWorkFactory(database)
    archived_at = datetime(2026, 2, 1, tzinfo=UTC)

    archived = await build_archive_branch_service(uow_factory, FixedClock(archived_at)).execute(
        TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID)
    )

    assert archived.id == TEST_BRANCH_ID
    assert archived.status is BranchStatus.ARCHIVED
    assert archived.archived_at == archived_at
    assert database.branches[TEST_BRANCH_ID].status is BranchStatus.ARCHIVED
    assert database.branches[second.id].status is BranchStatus.ACTIVE
    assert TEST_BUSINESS_ID in database.businesses
    assert database.commit_count == 1
    loaded = await build_get_branch_service(uow_factory).execute(
        TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID)
    )
    assert loaded.status is BranchStatus.ARCHIVED


async def test_archiving_branch_twice_fails() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database, status=BranchStatus.ARCHIVED)

    with pytest.raises(BranchArchivedError):
        await build_archive_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID))

    assert database.commit_count == 0


async def test_owner_cannot_archive_branch_belonging_to_another_business() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    foreign = seed_branch(database, business_id=UUID(int=55))

    with pytest.raises(BranchNotFoundError):
        await build_archive_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, foreign.id, actor=AuthenticatedActor(TEST_USER_ID))

    assert database.branches[foreign.id].status is BranchStatus.ACTIVE


async def test_non_owner_member_cannot_archive_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    member = build_membership(
        membership_id=UUID(int=56), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.memberships[member.id] = member

    with pytest.raises(BusinessPermissionDeniedError):
        await build_archive_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(OTHER_USER_ID))

    assert database.commit_count == 0


async def test_archived_business_cannot_archive_its_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database, status=BusinessStatus.ARCHIVED)
    seed_branch(database)

    with pytest.raises(BusinessArchivedError):
        await build_archive_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID))


async def test_archive_commit_failure_preserves_active_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(RuntimeError, match="Commit failed"):
        await build_archive_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database, fail_commit=True), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID))

    assert database.branches[TEST_BRANCH_ID].status is BranchStatus.ACTIVE
    assert database.commit_count == 0
