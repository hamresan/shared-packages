import asyncio
from uuid import uuid4

import pytest

from business.application.actor import AuthenticatedActor
from business.application.dto_membership import TransferOwnershipCommand
from business.domain.enums import MembershipRole, MembershipStatus
from business.domain.errors import BusinessNotFoundError
from tests.support.builders import TEST_BUSINESS_ID, TEST_USER_ID, build_business, build_membership
from tests.support.factories import build_transfer_ownership_service
from tests.support.membership_scenarios import clock, ids
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


@pytest.mark.asyncio
async def test_concurrent_transfers_preserve_single_owner(
    postgresql_environment: SqlAlchemyEnvironment,
) -> None:
    first_recipient, second_recipient = uuid4(), uuid4()
    async with postgresql_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.memberships.add(build_membership())
        await uow.memberships.add(
            build_membership(
                membership_id=first_recipient, user_id=uuid4(), role=MembershipRole.MANAGER
            )
        )
        await uow.memberships.add(
            build_membership(
                membership_id=second_recipient, user_id=uuid4(), role=MembershipRole.MEMBER
            )
        )
        await uow.commit()

    first = build_transfer_ownership_service(postgresql_environment.uow, clock(), ids(uuid4()))
    second = build_transfer_ownership_service(postgresql_environment.uow, clock(), ids(uuid4()))
    results = await asyncio.gather(
        first.execute(
            TransferOwnershipCommand(TEST_BUSINESS_ID, first_recipient),
            actor=AuthenticatedActor(TEST_USER_ID),
        ),
        second.execute(
            TransferOwnershipCommand(TEST_BUSINESS_ID, second_recipient),
            actor=AuthenticatedActor(TEST_USER_ID),
        ),
        return_exceptions=True,
    )
    assert sum(not isinstance(value, BaseException) for value in results) == 1
    assert sum(isinstance(value, BusinessNotFoundError) for value in results) == 1
    async with postgresql_environment.uow() as uow:
        assert await uow.memberships.count_active_owners(TEST_BUSINESS_ID) == 1
        memberships = await uow.memberships.list_for_business(TEST_BUSINESS_ID)
        assert (
            sum(
                item.role is MembershipRole.OWNER and item.status is MembershipStatus.ACTIVE
                for item in memberships
            )
            == 1
        )
