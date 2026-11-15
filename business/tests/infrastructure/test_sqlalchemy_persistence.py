from uuid import uuid4

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from business.application.dto import ListBranchesQuery
from business.application.dto_membership import InviteMemberCommand, SetMemberBranchAccessCommand
from business.domain.enums import BranchAccessScope, MembershipRole, MembershipStatus
from business.domain.errors import BranchNotFoundError
from business.infrastructure.persistence.sqlalchemy import (
    MembershipAuditModel,
    MembershipBranchAccessModel,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_MEMBERSHIP_ID,
    TEST_USER_ID,
    build_branch,
    build_business,
    build_membership,
)
from tests.support.factories import (
    build_get_branch_service,
    build_invite_member_service,
    build_list_branch_service,
    build_set_member_branch_access_service,
)
from tests.support.membership_scenarios import clock, ids, member_actor, owner_actor
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


@pytest.mark.asyncio
async def test_business_without_branches_and_repository_roundtrip(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.memberships.add(build_membership())
        await uow.commit()

    async with sqlalchemy_environment.uow() as uow:
        business = await uow.businesses.get_by_id(TEST_BUSINESS_ID)
        assert business is not None and business.name == "Muscat Bakery"
        assert (
            await uow.branches.list_for_business(TEST_BUSINESS_ID, city=None, country_code=None)
            == ()
        )
        assert len(await uow.memberships.list_by_user_id(TEST_USER_ID)) == 1
        assert await uow.memberships.count_active_owners(TEST_BUSINESS_ID) == 1


@pytest.mark.asyncio
async def test_branch_filters_and_scoped_member_visibility(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    other_branch_id = uuid4()
    from business.domain.value_objects import BranchAddress

    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.memberships.add(build_membership())
        await uow.memberships.add(
            build_membership(
                membership_id=uuid4(),
                user_id=OTHER_USER_ID,
                role=MembershipRole.MEMBER,
                branch_access_scope=BranchAccessScope.SELECTED,
            )
        )
        await uow.branches.add(
            build_branch(address=BranchAddress(country_code="OM", city="Muscat"))
        )
        await uow.branches.add(
            build_branch(
                branch_id=other_branch_id, address=BranchAddress(country_code="OM", city="Salalah")
            )
        )
        await uow.commit()

    listed = await build_list_branch_service(sqlalchemy_environment.uow).execute(
        ListBranchesQuery(TEST_BUSINESS_ID, city="muscat"), actor=owner_actor()
    )
    assert len(listed) == 1 and listed[0].id == TEST_BRANCH_ID
    empty = await build_list_branch_service(sqlalchemy_environment.uow).execute(
        ListBranchesQuery(TEST_BUSINESS_ID), actor=member_actor()
    )
    assert empty == ()
    async with sqlalchemy_environment.uow() as uow:
        member = await uow.memberships.get_by_business_and_user(TEST_BUSINESS_ID, OTHER_USER_ID)
    assert member is not None
    await build_set_member_branch_access_service(
        sqlalchemy_environment.uow, clock(), ids(uuid4())
    ).execute(
        SetMemberBranchAccessCommand(
            TEST_BUSINESS_ID, member.id, BranchAccessScope.SELECTED, (TEST_BRANCH_ID,)
        ),
        actor=owner_actor(),
    )
    listed = await build_list_branch_service(sqlalchemy_environment.uow).execute(
        ListBranchesQuery(TEST_BUSINESS_ID), actor=member_actor()
    )
    assert tuple(branch.id for branch in listed) == (TEST_BRANCH_ID,)
    with pytest.raises(BranchNotFoundError):
        await build_get_branch_service(sqlalchemy_environment.uow).execute(
            TEST_BUSINESS_ID, other_branch_id, actor=member_actor()
        )


@pytest.mark.asyncio
async def test_partial_unique_membership_index_and_reinvite(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.memberships.add(build_membership())
        await uow.commit()

    with pytest.raises(IntegrityError):
        async with sqlalchemy_environment.uow() as uow:
            await uow.memberships.add(build_membership(membership_id=uuid4()))
            await uow.commit()

    async with sqlalchemy_environment.uow() as uow:
        first = await uow.memberships.get_for_business(TEST_BUSINESS_ID, TEST_MEMBERSHIP_ID)
        assert first is not None
        first.revoke(revoked_at=clock().now())
        await uow.memberships.save(first)
        await uow.commit()

    async with sqlalchemy_environment.uow() as uow:
        await uow.memberships.add(build_membership(membership_id=uuid4()))
        await uow.commit()
    async with sqlalchemy_environment.uow() as uow:
        assert len(await uow.memberships.list_for_business(TEST_BUSINESS_ID)) == 2


@pytest.mark.asyncio
async def test_transaction_rollback_on_exception(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    with pytest.raises(RuntimeError):
        async with sqlalchemy_environment.uow() as uow:
            await uow.businesses.add(build_business())
            await uow.memberships.add(build_membership())
            raise RuntimeError("abort")
    async with sqlalchemy_environment.uow() as uow:
        assert await uow.businesses.get_by_id(TEST_BUSINESS_ID) is None


@pytest.mark.asyncio
async def test_invitation_commits_membership_and_audit(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.memberships.add(build_membership())
        await uow.commit()
    invited = await build_invite_member_service(
        sqlalchemy_environment.uow, clock(), ids(uuid4(), uuid4())
    ).execute(InviteMemberCommand(TEST_BUSINESS_ID, OTHER_USER_ID), actor=owner_actor())
    assert invited.status is MembershipStatus.INVITED
    async with sqlalchemy_environment.engine.connect() as connection:
        result = await connection.execute(select(MembershipAuditModel))
        assert len(result.all()) == 1


@pytest.mark.asyncio
async def test_membership_branch_fk_rejects_foreign_business(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    other_id = uuid4()
    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.businesses.add(build_business(business_id=other_id))
        await uow.memberships.add(build_membership())
        await uow.branches.add(build_branch(business_id=other_id))
        await uow.commit()
    with pytest.raises(IntegrityError):
        async with sqlalchemy_environment.engine.begin() as connection:
            await connection.execute(
                insert(MembershipBranchAccessModel).values(
                    membership_id=TEST_MEMBERSHIP_ID,
                    branch_id=TEST_BRANCH_ID,
                    business_id=TEST_BUSINESS_ID,
                )
            )
