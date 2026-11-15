from uuid import uuid4

import pytest

from business.application.actor import AuthenticatedActor
from business.application.dto import ListBranchesQuery
from business.application.dto_membership import (
    ChangeMemberRoleCommand,
    SetMemberBranchAccessCommand,
)
from business.domain.enums import BranchAccessScope, MembershipRole
from business.domain.errors import BusinessPermissionDeniedError, MembershipInvalidStateError
from tests.support.builders import OTHER_USER_ID, TEST_BRANCH_ID, TEST_BUSINESS_ID, build_membership
from tests.support.factories import (
    build_change_member_role_service,
    build_list_branch_service,
    build_list_memberships_service,
    build_set_member_branch_access_service,
)
from tests.support.fakes.unit_of_work import InMemoryBusinessUnitOfWorkFactory
from tests.support.membership_scenarios import (
    MEMBER_ID,
    clock,
    ids,
    owner_actor,
    setup_membership_database,
)
from tests.support.scenarios import seed_branch


@pytest.mark.asyncio
async def test_multiple_managers_are_allowed_and_can_manage_branches() -> None:
    database = setup_membership_database()
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    first = await build_change_member_role_service(factory, clock(), ids(uuid4())).execute(
        ChangeMemberRoleCommand(TEST_BUSINESS_ID, MEMBER_ID, MembershipRole.MANAGER),
        actor=owner_actor(),
    )
    assert first.branch_access_scope is BranchAccessScope.ALL
    another_id, another_user_id = uuid4(), uuid4()
    database.memberships[another_id] = build_membership(
        membership_id=another_id, user_id=another_user_id, role=MembershipRole.MANAGER
    )
    seed_branch(database)
    for user_id in (OTHER_USER_ID, another_user_id):
        actor = AuthenticatedActor(user_id)
        found = await build_list_branch_service(factory).execute(
            ListBranchesQuery(TEST_BUSINESS_ID), actor=actor
        )
        assert tuple(branch.id for branch in found) == (TEST_BRANCH_ID,)
        with pytest.raises(BusinessPermissionDeniedError):
            await build_list_memberships_service(factory).execute(TEST_BUSINESS_ID, actor=actor)


@pytest.mark.asyncio
async def test_manager_cannot_be_restricted_to_selected_branches() -> None:
    database = setup_membership_database()
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    await build_change_member_role_service(factory, clock(), ids(uuid4())).execute(
        ChangeMemberRoleCommand(TEST_BUSINESS_ID, MEMBER_ID, MembershipRole.MANAGER),
        actor=owner_actor(),
    )
    with pytest.raises(MembershipInvalidStateError):
        await build_set_member_branch_access_service(factory, clock(), ids(uuid4())).execute(
            SetMemberBranchAccessCommand(TEST_BUSINESS_ID, MEMBER_ID, BranchAccessScope.SELECTED),
            actor=owner_actor(),
        )
