from uuid import UUID

import pytest

from business.application import AuthenticatedActor, CreateBranchCommand, ListBranchesQuery
from business.domain import (
    BranchAddress,
    BranchStatus,
    BusinessArchivedError,
    BusinessNotFoundError,
    BusinessPermissionDeniedError,
    BusinessStatus,
    MembershipRole,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_TIME,
    TEST_USER_ID,
    build_create_branch_command,
    build_membership,
)
from tests.support.factories import build_create_branch_service, build_list_branch_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
    SequentialIdentifierGenerator,
)
from tests.support.scenarios import seed_owned_business


async def test_single_business_can_add_two_independent_branches() -> None:
    database = InMemoryBusinessDatabase()
    business = seed_owned_business(database)
    assert database.branches == {}
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1), UUID(int=2))),
    )
    actor = AuthenticatedActor(TEST_USER_ID)

    first = await service.execute(build_create_branch_command(name="Muscat"), actor=actor)
    second = await service.execute(
        build_create_branch_command(name="Salalah", city="Salalah"), actor=actor
    )

    assert {first.id, second.id} == set(database.branches)
    assert first.business_id == second.business_id == business.id
    assert first.name == "Muscat"
    assert second.address is not None and second.address.city == "Salalah"
    assert first.status is second.status is BranchStatus.ACTIVE
    assert len(database.businesses) == 1
    assert database.commit_count == 2


async def test_branch_creation_does_not_require_a_physical_address() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1),)),
    )

    branch = await service.execute(
        CreateBranchCommand(TEST_BUSINESS_ID, "Remote Operations", "UTC"),
        actor=AuthenticatedActor(TEST_USER_ID),
    )

    assert branch.address is None
    assert branch.contact is None
    assert branch.created_at == branch.updated_at == TEST_TIME
    assert database.branches[branch.id].timezone == "UTC"


async def test_two_businesses_manage_independent_single_branches() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    other_business_id = UUID(int=150)
    seed_owned_business(
        database,
        business_id=other_business_id,
        user_id=OTHER_USER_ID,
        membership_id=UUID(int=151),
    )
    uow_factory = InMemoryBusinessUnitOfWorkFactory(database)
    service = build_create_branch_service(
        uow_factory,
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=152), UUID(int=153))),
    )

    first = await service.execute(
        build_create_branch_command(), actor=AuthenticatedActor(TEST_USER_ID)
    )
    second = await service.execute(
        build_create_branch_command(business_id=other_business_id, name="Dubai"),
        actor=AuthenticatedActor(OTHER_USER_ID),
    )
    list_service = build_list_branch_service(uow_factory)

    first_visible = await list_service.execute(
        ListBranchesQuery(TEST_BUSINESS_ID), actor=AuthenticatedActor(TEST_USER_ID)
    )
    second_visible = await list_service.execute(
        ListBranchesQuery(other_business_id), actor=AuthenticatedActor(OTHER_USER_ID)
    )
    assert tuple(branch.id for branch in first_visible) == (first.id,)
    assert tuple(branch.id for branch in second_visible) == (second.id,)


async def test_branch_creation_normalizes_city_and_country() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1),)),
    )

    branch = await service.execute(
        CreateBranchCommand(
            business_id=TEST_BUSINESS_ID,
            name="  Main  ",
            timezone=" Asia/Muscat ",
            address=BranchAddress(country_code="om", city=" Muscat "),
        ),
        actor=AuthenticatedActor(TEST_USER_ID),
    )

    assert branch.name == "Main"
    assert branch.timezone == "Asia/Muscat"
    assert branch.address == BranchAddress(country_code="OM", city="Muscat")


async def test_active_member_cannot_create_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    member = build_membership(
        membership_id=UUID(int=20), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.memberships[member.id] = member
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1),)),
    )

    with pytest.raises(BusinessPermissionDeniedError):
        await service.execute(
            build_create_branch_command(), actor=AuthenticatedActor(OTHER_USER_ID)
        )

    assert database.branches == {}
    assert database.commit_count == 0


async def test_unrelated_user_cannot_create_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1),)),
    )

    with pytest.raises(BusinessNotFoundError):
        await service.execute(
            build_create_branch_command(), actor=AuthenticatedActor(OTHER_USER_ID)
        )

    assert database.branches == {}


async def test_archived_business_cannot_create_branch() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database, status=BusinessStatus.ARCHIVED)
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1),)),
    )

    with pytest.raises(BusinessArchivedError):
        await service.execute(build_create_branch_command(), actor=AuthenticatedActor(TEST_USER_ID))

    assert database.branches == {}


async def test_invalid_branch_details_fail_without_persistence() -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    service = build_create_branch_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1),)),
    )

    with pytest.raises(ValueError):
        await service.execute(
            build_create_branch_command(name=" "), actor=AuthenticatedActor(TEST_USER_ID)
        )

    assert database.branches == {}
    assert database.commit_count == 0


@pytest.mark.parametrize("failure", ["add", "commit"])
async def test_branch_persistence_failure_does_not_create_partial_branch(failure: str) -> None:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    uow_factory = InMemoryBusinessUnitOfWorkFactory(
        database, fail_branch_add=failure == "add", fail_commit=failure == "commit"
    )
    service = build_create_branch_service(
        uow_factory, FixedClock(TEST_TIME), SequentialIdentifierGenerator((UUID(int=1),))
    )

    with pytest.raises(RuntimeError):
        await service.execute(build_create_branch_command(), actor=AuthenticatedActor(TEST_USER_ID))

    assert database.branches == {}
    assert database.commit_count == 0
