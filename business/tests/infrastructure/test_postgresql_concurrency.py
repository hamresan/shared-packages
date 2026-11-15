import asyncio
from uuid import uuid4

import pytest

from business.application.actor import AuthenticatedActor
from business.domain.enums import MembershipRole, MembershipStatus
from business.domain.errors import BusinessNotFoundError, LastActiveOwnerError
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_MEMBERSHIP_ID,
    TEST_USER_ID,
    build_business,
    build_membership,
)
from tests.support.factories import build_revoke_membership_service
from tests.support.membership_scenarios import clock, ids
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


@pytest.mark.asyncio
async def test_concurrent_owner_revocations_cannot_remove_last_owner(
    postgresql_environment: SqlAlchemyEnvironment,
) -> None:
    second_membership_id = uuid4()
    async with postgresql_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.memberships.add(build_membership())
        await uow.memberships.add(
            build_membership(
                membership_id=second_membership_id, user_id=OTHER_USER_ID, role=MembershipRole.OWNER
            )
        )
        await uow.commit()

    first = build_revoke_membership_service(postgresql_environment.uow, clock(), ids(uuid4()))
    second = build_revoke_membership_service(postgresql_environment.uow, clock(), ids(uuid4()))
    results = await asyncio.gather(
        first.execute(
            TEST_BUSINESS_ID, second_membership_id, actor=AuthenticatedActor(TEST_USER_ID)
        ),
        second.execute(
            TEST_BUSINESS_ID, TEST_MEMBERSHIP_ID, actor=AuthenticatedActor(OTHER_USER_ID)
        ),
        return_exceptions=True,
    )
    assert sum(not isinstance(value, BaseException) for value in results) == 1
    assert (
        sum(isinstance(value, (LastActiveOwnerError, BusinessNotFoundError)) for value in results)
        == 1
    )
    async with postgresql_environment.uow() as uow:
        assert await uow.memberships.count_active_owners(TEST_BUSINESS_ID) == 1
        memberships = await uow.memberships.list_for_business(TEST_BUSINESS_ID)
        assert sum(item.status is MembershipStatus.REVOKED for item in memberships) == 1
