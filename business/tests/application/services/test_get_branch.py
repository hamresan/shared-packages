from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.domain import BranchNotFoundError, BranchStatus, BusinessNotFoundError, MembershipRole
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_USER_ID,
    build_membership,
)
from tests.support.factories import build_get_branch_service
from tests.support.fakes import InMemoryBusinessDatabase, InMemoryBusinessUnitOfWorkFactory
from tests.support.scenarios import seed_branch, seed_owned_business


async def test_owner_and_active_member_can_read_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    branch = seed_branch(database)
    member = build_membership(
        membership_id=UUID(int=33), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.memberships[member.id] = member
    service = build_get_branch_service(InMemoryBusinessUnitOfWorkFactory(database))

    owner_result = await service.execute(
        TEST_BUSINESS_ID, branch.id, actor=AuthenticatedActor(TEST_USER_ID)
    )
    member_result = await service.execute(
        TEST_BUSINESS_ID, branch.id, actor=AuthenticatedActor(OTHER_USER_ID)
    )

    assert owner_result.id == member_result.id == TEST_BRANCH_ID


async def test_archived_branch_remains_readable() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database, status=BranchStatus.ARCHIVED)

    branch = await build_get_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
        TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID)
    )

    assert branch.status is BranchStatus.ARCHIVED
    assert branch.id == TEST_BRANCH_ID


async def test_other_business_branch_is_not_visible_under_authorized_scope() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    foreign_business_id = UUID(int=78)
    foreign = seed_branch(database, business_id=foreign_business_id)
    service = build_get_branch_service(InMemoryBusinessUnitOfWorkFactory(database))

    with pytest.raises(BranchNotFoundError):
        await service.execute(TEST_BUSINESS_ID, foreign.id, actor=AuthenticatedActor(TEST_USER_ID))


async def test_unrelated_actor_cannot_read_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(BusinessNotFoundError):
        await build_get_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(OTHER_USER_ID)
        )


async def test_missing_branch_raises_without_affecting_business() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)

    with pytest.raises(BranchNotFoundError):
        await build_get_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            TEST_BUSINESS_ID, UUID(int=99), actor=AuthenticatedActor(TEST_USER_ID)
        )

    assert database.commit_count == 0


async def test_branch_read_is_detached_from_stored_entity() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    loaded = await build_get_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
        TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=AuthenticatedActor(TEST_USER_ID)
    )

    loaded.name = "Unsaved"

    assert database.branches[TEST_BRANCH_ID].name == "Main Branch"
