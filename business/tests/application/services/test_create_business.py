from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.domain import MembershipRole, MembershipStatus
from tests.support.builders import TEST_TIME, TEST_USER_ID, build_create_command
from tests.support.factories import build_create_service, build_get_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
    SequentialIdentifierGenerator,
)


async def test_creator_owns_two_businesses_without_creating_branches() -> None:
    database = InMemoryBusinessDatabase()
    uow_factory = InMemoryBusinessUnitOfWorkFactory(database)
    identifiers = SequentialIdentifierGenerator(tuple(UUID(int=index) for index in range(1, 5)))
    service = build_create_service(uow_factory, FixedClock(TEST_TIME), identifiers)
    actor = AuthenticatedActor(user_id=TEST_USER_ID)

    first = await service.execute(build_create_command("First"), actor=actor)
    second = await service.execute(build_create_command("Second"), actor=actor)

    assert first.id != second.id
    assert {first.id, second.id} == set(database.businesses)
    assert {membership.business_id for membership in database.memberships.values()} == {
        first.id,
        second.id,
    }
    assert all(membership.user_id == TEST_USER_ID for membership in database.memberships.values())
    assert all(
        membership.role is MembershipRole.OWNER for membership in database.memberships.values()
    )
    assert all(
        membership.status is MembershipStatus.ACTIVE for membership in database.memberships.values()
    )
    assert database.commit_count == 2
    assert (await build_get_service(uow_factory).execute(first.id, actor=actor)).name == "First"


async def test_create_normalizes_settings_and_uses_same_time_for_owner_membership() -> None:
    database = InMemoryBusinessDatabase()
    ids = SequentialIdentifierGenerator((UUID(int=11), UUID(int=12)))
    service = build_create_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME), ids
    )

    business = await service.execute(build_create_command(), actor=AuthenticatedActor(TEST_USER_ID))
    membership = next(iter(database.memberships.values()))

    assert business.name == "My Business"
    assert business.country_code == "OM"
    assert business.default_currency_code == "OMR"
    assert business.business_type is None
    assert membership.business_id == business.id
    assert business.created_at == business.updated_at == membership.created_at == TEST_TIME


async def test_invalid_creation_cannot_write_a_business_or_membership() -> None:
    database = InMemoryBusinessDatabase()
    service = build_create_service(
        InMemoryBusinessUnitOfWorkFactory(database),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1), UUID(int=2))),
    )

    with pytest.raises(ValueError):
        await service.execute(build_create_command(" "), actor=AuthenticatedActor(TEST_USER_ID))

    assert database.businesses == {}
    assert database.memberships == {}
    assert database.commit_count == 0


async def test_membership_write_failure_rolls_back_business_creation() -> None:
    database = InMemoryBusinessDatabase()
    service = build_create_service(
        InMemoryBusinessUnitOfWorkFactory(database, fail_membership_add=True),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1), UUID(int=2))),
    )

    with pytest.raises(RuntimeError, match="Membership write failed"):
        await service.execute(build_create_command(), actor=AuthenticatedActor(TEST_USER_ID))

    assert database.businesses == {}
    assert database.memberships == {}
    assert database.commit_count == 0


async def test_commit_failure_does_not_persist_a_business_without_its_owner() -> None:
    database = InMemoryBusinessDatabase()
    service = build_create_service(
        InMemoryBusinessUnitOfWorkFactory(database, fail_commit=True),
        FixedClock(TEST_TIME),
        SequentialIdentifierGenerator((UUID(int=1), UUID(int=2))),
    )

    with pytest.raises(RuntimeError, match="Commit failed"):
        await service.execute(build_create_command(), actor=AuthenticatedActor(TEST_USER_ID))

    assert database.businesses == {}
    assert database.memberships == {}
    assert database.commit_count == 0
