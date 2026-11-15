from datetime import UTC, datetime
from uuid import UUID

import pytest

from business.application import AuthenticatedActor, UpdateBranchCommand
from business.domain import (
    BranchAddress,
    BranchArchivedError,
    BranchContact,
    BranchNotFoundError,
    BranchStatus,
    BusinessArchivedError,
    BusinessNotFoundError,
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
from tests.support.factories import build_update_branch_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
)
from tests.support.scenarios import seed_branch, seed_owned_business


async def test_owner_updates_branch_details_without_reparenting() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    changed_at = datetime(2026, 2, 1, tzinfo=UTC)
    service = build_update_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(changed_at)
    )

    branch = await service.execute(
        UpdateBranchCommand(
            TEST_BUSINESS_ID,
            TEST_BRANCH_ID,
            "  Salalah Branch ",
            "Asia/Muscat",
            BranchAddress(country_code="om", city=" Salalah "),
            BranchContact(phone=" +96812345678 "),
        ),
        actor=AuthenticatedActor(TEST_USER_ID),
    )

    assert branch.business_id == TEST_BUSINESS_ID
    assert branch.id == TEST_BRANCH_ID
    assert branch.name == "Salalah Branch"
    assert branch.address == BranchAddress(country_code="OM", city="Salalah")
    assert branch.contact == BranchContact(phone="+96812345678")
    assert branch.updated_at == changed_at
    assert database.branches[TEST_BRANCH_ID].name == "Salalah Branch"
    assert database.commit_count == 1


async def test_cross_business_branch_reparenting_attempt_is_rejected() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    foreign_business_id = UUID(int=50)
    branch = seed_branch(database, business_id=foreign_business_id)
    service = build_update_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
    )

    with pytest.raises(BranchNotFoundError):
        await service.execute(
            UpdateBranchCommand(TEST_BUSINESS_ID, branch.id, "Hijack", "UTC", None, None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.branches[branch.id].business_id == foreign_business_id
    assert database.branches[branch.id].name == "Main Branch"
    assert database.commit_count == 0


async def test_member_cannot_update_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    member = build_membership(
        membership_id=UUID(int=51), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.memberships[member.id] = member
    service = build_update_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
    )

    with pytest.raises(BusinessPermissionDeniedError):
        await service.execute(
            UpdateBranchCommand(TEST_BUSINESS_ID, TEST_BRANCH_ID, "Member", "UTC", None, None),
            actor=AuthenticatedActor(OTHER_USER_ID),
        )

    assert database.commit_count == 0


async def test_outsider_cannot_update_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(BusinessNotFoundError):
        await build_update_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBranchCommand(TEST_BUSINESS_ID, TEST_BRANCH_ID, "Outsider", "UTC", None, None),
            actor=AuthenticatedActor(OTHER_USER_ID),
        )

    assert database.commit_count == 0


async def test_update_cannot_modify_archived_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database, status=BranchStatus.ARCHIVED)

    with pytest.raises(BranchArchivedError):
        await build_update_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBranchCommand(TEST_BUSINESS_ID, TEST_BRANCH_ID, "Updated", "UTC", None, None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.branches[TEST_BRANCH_ID].status is BranchStatus.ARCHIVED


async def test_update_cannot_modify_branch_of_archived_business() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database, status=BusinessStatus.ARCHIVED)
    seed_branch(database)

    with pytest.raises(BusinessArchivedError):
        await build_update_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBranchCommand(TEST_BUSINESS_ID, TEST_BRANCH_ID, "Updated", "UTC", None, None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )


async def test_invalid_timezone_rejected_without_change() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(ValueError):
        await build_update_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBranchCommand(
                TEST_BUSINESS_ID, TEST_BRANCH_ID, "New", "Mars/Unknown", None, None
            ),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.branches[TEST_BRANCH_ID].name == "Main Branch"
    assert database.commit_count == 0


async def test_failed_commit_does_not_modify_stored_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(RuntimeError, match="Commit failed"):
        await build_update_branch_service(
            InMemoryBusinessUnitOfWorkFactory(database, fail_commit=True), FixedClock(TEST_TIME)
        ).execute(
            UpdateBranchCommand(TEST_BUSINESS_ID, TEST_BRANCH_ID, "Failed", "UTC", None, None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.branches[TEST_BRANCH_ID].name == "Main Branch"
    assert database.commit_count == 0
