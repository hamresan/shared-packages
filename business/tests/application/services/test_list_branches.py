from uuid import UUID

import pytest

from business.application import AuthenticatedActor, ListBranchesQuery
from business.domain import BranchAddress, BranchStatus, BusinessNotFoundError
from tests.support.builders import OTHER_USER_ID, TEST_BUSINESS_ID, TEST_USER_ID
from tests.support.factories import build_list_branch_service
from tests.support.fakes import InMemoryBusinessDatabase, InMemoryBusinessUnitOfWorkFactory
from tests.support.scenarios import seed_branch, seed_owned_business


async def test_business_with_zero_branches_returns_empty_list() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)

    branches = await build_list_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
        ListBranchesQuery(TEST_BUSINESS_ID), actor=AuthenticatedActor(TEST_USER_ID)
    )

    assert branches == ()
    assert database.commit_count == 0


async def test_one_business_lists_multiple_branches_but_not_foreign_branches() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    first = seed_branch(database, address=BranchAddress(country_code="OM", city="Muscat"))
    second = seed_branch(
        database,
        branch_id=UUID(int=2),
        address=BranchAddress(country_code="OM", city="Salalah"),
        status=BranchStatus.ARCHIVED,
    )
    seed_branch(database, branch_id=UUID(int=3), business_id=UUID(int=30))

    branches = await build_list_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
        ListBranchesQuery(TEST_BUSINESS_ID), actor=AuthenticatedActor(TEST_USER_ID)
    )

    assert {branch.id for branch in branches} == {first.id, second.id}
    assert any(branch.status is BranchStatus.ARCHIVED for branch in branches)


async def test_branch_list_filters_city_case_insensitively_and_country() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    first = seed_branch(database, address=BranchAddress(country_code="OM", city="Muscat"))
    seed_branch(
        database, branch_id=UUID(int=2), address=BranchAddress(country_code="OM", city="Salalah")
    )
    seed_branch(
        database, branch_id=UUID(int=3), address=BranchAddress(country_code="AE", city="Muscat")
    )
    seed_branch(database, branch_id=UUID(int=4))
    service = build_list_branch_service(InMemoryBusinessUnitOfWorkFactory(database))

    branches = await service.execute(
        ListBranchesQuery(TEST_BUSINESS_ID, city="  MUSCAT ", country_code="om"),
        actor=AuthenticatedActor(TEST_USER_ID),
    )

    assert tuple(branch.id for branch in branches) == (first.id,)


async def test_unrelated_user_cannot_list_branches() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    seed_branch(database)

    with pytest.raises(BusinessNotFoundError):
        await build_list_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            ListBranchesQuery(TEST_BUSINESS_ID), actor=AuthenticatedActor(OTHER_USER_ID)
        )


async def test_invalid_city_filter_rejected_before_repository_read() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)

    with pytest.raises(ValueError):
        await build_list_branch_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            ListBranchesQuery(TEST_BUSINESS_ID, city="x" * 121),
            actor=AuthenticatedActor(TEST_USER_ID),
        )
