from uuid import UUID

from business.application import BusinessAuthorizationReader
from business.application.authorization.dto import MembershipAuthorizationInfo
from business.domain.enums import BranchAccessScope, MembershipRole, MembershipStatus
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_USER_ID,
    build_branch,
    build_business,
    build_membership,
)
from tests.support.factories import build_authorization_service
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


async def test_sql_authorization_queries_enforce_business_and_selected_branch_scope(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    other_business_id = UUID(int=90)
    other_branch_id = UUID(int=91)
    selected_membership_id = UUID(int=92)
    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.businesses.add(build_business(business_id=other_business_id))
        await uow.branches.add(build_branch())
        await uow.branches.add(
            build_branch(branch_id=other_branch_id, business_id=other_business_id)
        )
        await uow.memberships.add(build_membership())
        await uow.memberships.add(
            build_membership(
                membership_id=selected_membership_id,
                user_id=OTHER_USER_ID,
                role=MembershipRole.MEMBER,
                branch_access_scope=BranchAccessScope.SELECTED,
            )
        )
        await uow.membership_branch_access.replace(selected_membership_id, (TEST_BRANCH_ID,))
        await uow.commit()

    service: BusinessAuthorizationReader = build_authorization_service(sqlalchemy_environment.uow)
    info = await service.get_membership(TEST_BUSINESS_ID, OTHER_USER_ID)
    assert isinstance(info, MembershipAuthorizationInfo)
    assert info.role is MembershipRole.MEMBER and info.status is MembershipStatus.ACTIVE
    assert not await service.has_role(
        TEST_BUSINESS_ID, OTHER_USER_ID, frozenset({MembershipRole.OWNER, MembershipRole.MANAGER})
    )
    assert await service.has_role(TEST_BUSINESS_ID, TEST_USER_ID, frozenset({MembershipRole.OWNER}))
    assert await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, OTHER_USER_ID)
    assert not await service.can_access_branch(TEST_BUSINESS_ID, other_branch_id, OTHER_USER_ID)
    assert not await service.can_access_branch(other_business_id, TEST_BRANCH_ID, TEST_USER_ID)
    assert not await service.has_role(
        other_business_id, TEST_USER_ID, frozenset({MembershipRole.OWNER})
    )


async def test_sql_invited_and_revoked_memberships_do_not_grant_authorization(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    invited_user = UUID(int=93)
    revoked_user = UUID(int=94)
    async with sqlalchemy_environment.uow() as uow:
        await uow.businesses.add(build_business())
        await uow.branches.add(build_branch())
        await uow.memberships.add(build_membership())
        await uow.memberships.add(
            build_membership(
                membership_id=UUID(int=95),
                user_id=invited_user,
                status=MembershipStatus.INVITED,
            )
        )
        await uow.memberships.add(
            build_membership(
                membership_id=UUID(int=96),
                user_id=revoked_user,
                status=MembershipStatus.REVOKED,
                role=MembershipRole.MEMBER,
            )
        )
        await uow.commit()

    service = build_authorization_service(sqlalchemy_environment.uow)
    invited = await service.get_membership(TEST_BUSINESS_ID, invited_user)
    assert invited is not None and invited.status is MembershipStatus.INVITED
    assert await service.get_membership(TEST_BUSINESS_ID, revoked_user) is None
    for user_id in (invited_user, revoked_user):
        assert not await service.has_role(
            TEST_BUSINESS_ID, user_id, frozenset({MembershipRole.OWNER})
        )
        assert not await service.can_access_branch(TEST_BUSINESS_ID, TEST_BRANCH_ID, user_id)
