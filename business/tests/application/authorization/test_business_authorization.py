from dataclasses import replace
from uuid import UUID

import pytest

from business.application import BusinessAuthorizationReader
from business.bootstrap import BusinessApplicationFactory
from business.domain.enums import (
    BranchAccessScope,
    BranchStatus,
    BusinessStatus,
    MembershipRole,
    MembershipStatus,
)
from business.infrastructure.clock import SystemClock
from business.infrastructure.identifiers import UuidIdentifierGenerator
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_MEMBERSHIP_ID,
    TEST_USER_ID,
    build_membership,
)
from tests.support.factories import build_authorization_service
from tests.support.fakes import InMemoryBusinessDatabase, InMemoryBusinessUnitOfWorkFactory
from tests.support.scenarios import seed_branch, seed_owned_business


@pytest.mark.parametrize("role", list(MembershipRole))
async def test_active_role_checks_and_immutable_membership_summary(role: MembershipRole) -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    database.memberships[TEST_MEMBERSHIP_ID] = build_membership(role=role)
    service: BusinessAuthorizationReader = build_authorization_service(
        InMemoryBusinessUnitOfWorkFactory(database)
    )

    summary = await service.get_membership(TEST_BUSINESS_ID, TEST_USER_ID)

    assert summary is not None
    assert summary.role is role and summary.status is MembershipStatus.ACTIVE
    assert summary.business_id == TEST_BUSINESS_ID and summary.user_id == TEST_USER_ID
    assert replace(summary, role=MembershipRole.OWNER) is not summary
    assert await service.has_role(TEST_BUSINESS_ID, TEST_USER_ID, frozenset({role}))
    assert not await service.has_role(TEST_BUSINESS_ID, TEST_USER_ID, frozenset())
    assert not await service.has_role(
        TEST_BUSINESS_ID, TEST_USER_ID, frozenset(set(MembershipRole) - {role})
    )
    assert database.commit_count == 0


@pytest.mark.parametrize("status", [MembershipStatus.INVITED, MembershipStatus.REVOKED])
async def test_non_active_membership_never_grants_access(status: MembershipStatus) -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    database.memberships[TEST_MEMBERSHIP_ID] = build_membership(status=status)
    service = build_authorization_service(InMemoryBusinessUnitOfWorkFactory(database))

    assert not await service.has_role(
        TEST_BUSINESS_ID, TEST_USER_ID, frozenset({MembershipRole.OWNER})
    )
    assert not await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, TEST_USER_ID)
    summary = await service.get_membership(TEST_BUSINESS_ID, TEST_USER_ID)
    if status is MembershipStatus.INVITED:
        assert summary is not None and summary.status is MembershipStatus.INVITED
    else:
        assert summary is None


async def test_branch_access_respects_selected_scope_and_tenant() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)
    other_branch_id = UUID(int=51)
    seed_branch(database, branch_id=other_branch_id)
    foreign_business_id = UUID(int=52)
    foreign_branch_id = UUID(int=53)
    seed_owned_business(
        database,
        business_id=foreign_business_id,
        user_id=OTHER_USER_ID,
        membership_id=UUID(int=55),
    )
    seed_branch(database, business_id=foreign_business_id, branch_id=foreign_branch_id)
    selected_member_id = UUID(int=54)
    database.memberships[selected_member_id] = build_membership(
        membership_id=selected_member_id,
        user_id=OTHER_USER_ID,
        role=MembershipRole.MEMBER,
        branch_access_scope=BranchAccessScope.SELECTED,
    )
    service = build_authorization_service(InMemoryBusinessUnitOfWorkFactory(database))

    assert not await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, OTHER_USER_ID)
    database.membership_branch_ids[selected_member_id] = (TEST_BRANCH_ID,)
    assert await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, OTHER_USER_ID)
    assert not await service.can_access_branch(TEST_BUSINESS_ID, other_branch_id, OTHER_USER_ID)
    assert not await service.can_access_branch(TEST_BUSINESS_ID, foreign_branch_id, OTHER_USER_ID)
    assert not await service.can_access_branch(foreign_business_id, TEST_BRANCH_ID, OTHER_USER_ID)
    assert await service.can_access_branch(TEST_BUSINESS_ID, other_branch_id, TEST_USER_ID)


async def test_missing_and_archived_resources_follow_existing_read_semantics() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database, status=BusinessStatus.ARCHIVED)
    seed_branch(database, status=BranchStatus.ARCHIVED)
    service = build_authorization_service(InMemoryBusinessUnitOfWorkFactory(database))

    assert await service.has_role(TEST_BUSINESS_ID, TEST_USER_ID, frozenset({MembershipRole.OWNER}))
    assert await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, TEST_USER_ID)
    assert not await service.can_access_branch(TEST_BUSINESS_ID, UUID(int=77), TEST_USER_ID)
    assert await service.get_membership(UUID(int=78), TEST_USER_ID) is None
    assert not await service.has_role(UUID(int=78), TEST_USER_ID, frozenset(MembershipRole))
    assert not await service.can_access_branch(UUID(int=78), TEST_BRANCH_ID, TEST_USER_ID)
    assert await service.get_membership(TEST_BUSINESS_ID, OTHER_USER_ID) is None


async def test_all_scope_allows_members_and_branchless_business_denies_branch_query() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    member_id = UUID(int=79)
    database.memberships[member_id] = build_membership(
        membership_id=member_id,
        user_id=OTHER_USER_ID,
        role=MembershipRole.MEMBER,
        branch_access_scope=BranchAccessScope.ALL,
    )
    service = build_authorization_service(InMemoryBusinessUnitOfWorkFactory(database))

    assert not await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, OTHER_USER_ID)
    seed_branch(database)
    assert await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, OTHER_USER_ID)


async def test_application_factory_exposes_public_authorization_contract() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    factory = BusinessApplicationFactory(
        InMemoryBusinessUnitOfWorkFactory(database), SystemClock(), UuidIdentifierGenerator()
    )

    service: BusinessAuthorizationReader = factory.authorization()

    assert await service.has_role(TEST_BUSINESS_ID, TEST_USER_ID, frozenset({MembershipRole.OWNER}))
