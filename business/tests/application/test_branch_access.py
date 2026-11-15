from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.application.branch_access import BranchScopePolicy
from business.domain import (
    BranchNotFoundError,
    BusinessArchivedError,
    BusinessNotFoundError,
    BusinessPermissionDeniedError,
    BusinessStatus,
    MembershipRole,
    MembershipStatus,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_USER_ID,
    build_branch,
    build_business,
    build_membership,
)
from tests.support.factories import build_branch_access
from tests.support.fakes import InMemoryBusinessDatabase, InMemoryBusinessUnitOfWorkFactory


async def test_active_owner_can_read_and_modify_branches() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    async with InMemoryBusinessUnitOfWorkFactory(database)() as unit_of_work:
        access = build_branch_access()
        actor = AuthenticatedActor(TEST_USER_ID)
        assert (await access.require_readable(unit_of_work, business.id, actor)).id == business.id
        assert (await access.require_writable(unit_of_work, business.id, actor)).id == business.id


async def test_active_member_can_read_but_not_mutate_branches() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    member = build_membership(user_id=OTHER_USER_ID, role=MembershipRole.MEMBER)
    database.businesses[business.id] = business
    database.memberships[member.id] = member
    actor = AuthenticatedActor(OTHER_USER_ID)

    async with InMemoryBusinessUnitOfWorkFactory(database)() as unit_of_work:
        access = build_branch_access()
        assert (await access.require_readable(unit_of_work, business.id, actor)).id == business.id
        with pytest.raises(BusinessPermissionDeniedError):
            await access.require_writable(unit_of_work, business.id, actor)


async def test_archived_business_is_readable_but_cannot_mutate_branches() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business(status=BusinessStatus.ARCHIVED)
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner
    actor = AuthenticatedActor(TEST_USER_ID)

    async with InMemoryBusinessUnitOfWorkFactory(database)() as unit_of_work:
        access = build_branch_access()
        assert (await access.require_readable(unit_of_work, business.id, actor)).id == business.id
        with pytest.raises(BusinessArchivedError):
            await access.require_writable(unit_of_work, business.id, actor)


async def test_nonexistent_business_is_not_visible_even_with_orphaned_membership() -> None:
    database = InMemoryBusinessDatabase()
    membership = build_membership()
    database.memberships[membership.id] = membership

    async with InMemoryBusinessUnitOfWorkFactory(database)() as unit_of_work:
        with pytest.raises(BusinessNotFoundError):
            await build_branch_access().require_readable(
                unit_of_work, TEST_BUSINESS_ID, AuthenticatedActor(TEST_USER_ID)
            )


@pytest.mark.parametrize("status", [MembershipStatus.INVITED, MembershipStatus.REVOKED])
async def test_inactive_membership_cannot_read_branches(status: MembershipStatus) -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    membership = build_membership(status=status)
    database.businesses[business.id] = business
    database.memberships[membership.id] = membership

    async with InMemoryBusinessUnitOfWorkFactory(database)() as unit_of_work:
        with pytest.raises(BusinessNotFoundError):
            await build_branch_access().require_readable(
                unit_of_work, business.id, AuthenticatedActor(TEST_USER_ID)
            )


async def test_outsider_cannot_read_or_mutate_branches() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    async with InMemoryBusinessUnitOfWorkFactory(database)() as unit_of_work:
        access = build_branch_access()
        actor = AuthenticatedActor(OTHER_USER_ID)
        with pytest.raises(BusinessNotFoundError):
            await access.require_readable(unit_of_work, business.id, actor)
        with pytest.raises(BusinessNotFoundError):
            await access.require_writable(unit_of_work, business.id, actor)


def test_branch_scope_policy_rejects_a_branch_from_another_business() -> None:
    policy = BranchScopePolicy()
    branch = build_branch()

    assert policy.require_for_business(branch, TEST_BUSINESS_ID) is branch
    with pytest.raises(BranchNotFoundError):
        policy.require_for_business(branch, UUID(int=99))
    with pytest.raises(BranchNotFoundError):
        policy.require_for_business(None, TEST_BUSINESS_ID)
