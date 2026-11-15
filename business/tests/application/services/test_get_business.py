from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.domain import BusinessNotFoundError, MembershipRole, MembershipStatus
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_USER_ID,
    build_business,
    build_membership,
)
from tests.support.factories import build_get_service
from tests.support.fakes import InMemoryBusinessDatabase, InMemoryBusinessUnitOfWorkFactory


async def test_active_owner_and_member_can_read_business() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    member = build_membership(
        membership_id=UUID(int=3), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner
    database.memberships[member.id] = member
    service = build_get_service(InMemoryBusinessUnitOfWorkFactory(database))

    owner_result = await service.execute(business.id, actor=AuthenticatedActor(TEST_USER_ID))
    member_result = await service.execute(business.id, actor=AuthenticatedActor(OTHER_USER_ID))

    assert owner_result.id == business.id
    assert member_result.id == business.id


async def test_an_outsider_cannot_read_an_existing_business() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    with pytest.raises(BusinessNotFoundError):
        await build_get_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            TEST_BUSINESS_ID, actor=AuthenticatedActor(OTHER_USER_ID)
        )


@pytest.mark.parametrize("status", [MembershipStatus.INVITED, MembershipStatus.REVOKED])
async def test_inactive_members_cannot_read_business(status: MembershipStatus) -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    membership = build_membership(status=status)
    database.businesses[business.id] = business
    database.memberships[membership.id] = membership

    with pytest.raises(BusinessNotFoundError):
        await build_get_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            TEST_BUSINESS_ID, actor=AuthenticatedActor(TEST_USER_ID)
        )


async def test_nonexistent_business_is_not_visible_to_owner() -> None:
    database = InMemoryBusinessDatabase()
    membership = build_membership()
    database.memberships[membership.id] = membership

    with pytest.raises(BusinessNotFoundError):
        await build_get_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
            TEST_BUSINESS_ID, actor=AuthenticatedActor(TEST_USER_ID)
        )


async def test_read_returns_a_copy_not_the_database_entity() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    membership = build_membership()
    database.businesses[business.id] = business
    database.memberships[membership.id] = membership
    loaded = await build_get_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
        business.id, actor=AuthenticatedActor(TEST_USER_ID)
    )

    loaded.name = "Unsaved Change"

    assert database.businesses[business.id].name == "Muscat Bakery"
