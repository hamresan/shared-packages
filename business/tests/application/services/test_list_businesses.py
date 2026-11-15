from uuid import UUID

from business.application import AuthenticatedActor
from business.domain.enums import MembershipStatus
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_USER_ID,
    build_business,
    build_membership,
)
from tests.support.factories import build_list_service
from tests.support.fakes import InMemoryBusinessDatabase, InMemoryBusinessUnitOfWorkFactory


async def test_list_only_returns_businesses_for_active_membership() -> None:
    database = InMemoryBusinessDatabase()
    first_id, second_id, hidden_id = TEST_BUSINESS_ID, UUID(int=2), UUID(int=3)
    for business in (
        build_business(business_id=first_id, name="First"),
        build_business(business_id=second_id, name="Second"),
        build_business(business_id=hidden_id, name="Hidden"),
    ):
        database.businesses[business.id] = business
    for membership in (
        build_membership(business_id=first_id),
        build_membership(membership_id=UUID(int=10), business_id=second_id),
        build_membership(
            membership_id=UUID(int=11),
            business_id=hidden_id,
            status=MembershipStatus.REVOKED,
        ),
        build_membership(membership_id=UUID(int=12), business_id=hidden_id, user_id=OTHER_USER_ID),
    ):
        database.memberships[membership.id] = membership

    result = await build_list_service(InMemoryBusinessUnitOfWorkFactory(database)).execute(
        actor=AuthenticatedActor(TEST_USER_ID)
    )

    assert {business.id for business in result} == {first_id, second_id}
    assert database.commit_count == 0


async def test_list_is_empty_for_actor_without_memberships() -> None:
    service = build_list_service(InMemoryBusinessUnitOfWorkFactory(InMemoryBusinessDatabase()))

    assert await service.execute(actor=AuthenticatedActor(TEST_USER_ID)) == ()
