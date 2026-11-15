from uuid import UUID

import pytest

from business.application import AuthenticatedActor, UpdateBusinessCommand
from business.domain import BusinessNotFoundError
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_TIME,
    TEST_USER_ID,
    build_business,
    build_membership,
)
from tests.support.factories import (
    build_archive_service,
    build_get_service,
    build_list_service,
    build_update_service,
)
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
)


async def test_membership_in_one_business_does_not_grant_access_to_another() -> None:
    database = InMemoryBusinessDatabase()
    second_business_id = UUID(int=22)
    first = build_business(business_id=TEST_BUSINESS_ID, name="First")
    second = build_business(business_id=second_business_id, name="Second")
    owner_first = build_membership(user_id=TEST_USER_ID)
    owner_second = build_membership(
        membership_id=UUID(int=23), business_id=second_business_id, user_id=OTHER_USER_ID
    )
    database.businesses[first.id] = first
    database.businesses[second.id] = second
    database.memberships[owner_first.id] = owner_first
    database.memberships[owner_second.id] = owner_second
    uow_factory = InMemoryBusinessUnitOfWorkFactory(database)
    actor = AuthenticatedActor(TEST_USER_ID)

    visible = await build_list_service(uow_factory).execute(actor=actor)
    assert {business.id for business in visible} == {TEST_BUSINESS_ID}
    with pytest.raises(BusinessNotFoundError):
        await build_get_service(uow_factory).execute(second_business_id, actor=actor)
    with pytest.raises(BusinessNotFoundError):
        await build_update_service(uow_factory, FixedClock(TEST_TIME)).execute(
            UpdateBusinessCommand(second_business_id, "Not Authorized", None), actor=actor
        )
    with pytest.raises(BusinessNotFoundError):
        await build_archive_service(uow_factory, FixedClock(TEST_TIME)).execute(
            second_business_id, actor=actor
        )

    assert database.businesses[second_business_id].name == "Second"
    assert database.commit_count == 0
