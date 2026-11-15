from uuid import uuid4

import pytest

from business.application.dto import ListBranchesQuery
from business.application.dto_membership import (
    ChangeMemberRoleCommand,
    InviteMemberCommand,
    SetMemberBranchAccessCommand,
)
from business.domain.enums import (
    BranchAccessScope,
    MembershipAuditAction,
    MembershipRole,
    MembershipStatus,
)
from business.domain.errors import (
    BranchNotFoundError,
    BusinessPermissionDeniedError,
    LastActiveOwnerError,
    MembershipAlreadyExistsError,
    MembershipInvalidStateError,
    MembershipNotFoundError,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_MEMBERSHIP_ID,
)
from tests.support.factories import (
    build_accept_membership_service,
    build_change_member_role_service,
    build_get_branch_service,
    build_invite_member_service,
    build_list_branch_service,
    build_list_memberships_service,
    build_revoke_membership_service,
    build_set_member_branch_access_service,
)
from tests.support.fakes.unit_of_work import InMemoryBusinessUnitOfWorkFactory
from tests.support.membership_scenarios import (
    AUDIT_ID,
    FOREIGN_BUSINESS_ID,
    MEMBER_ID,
    OTHER_BRANCH_ID,
    clock,
    ids,
    member_actor,
    owner_actor,
    seed_member,
    setup_membership_database,
)
from tests.support.scenarios import seed_branch


@pytest.mark.asyncio
async def test_invite_accept_and_audit_transaction() -> None:
    database = setup_membership_database(include_member=False)
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    invited = await build_invite_member_service(factory, clock(), ids(MEMBER_ID, AUDIT_ID)).execute(
        InviteMemberCommand(TEST_BUSINESS_ID, OTHER_USER_ID), actor=owner_actor()
    )
    assert invited.status is MembershipStatus.INVITED
    assert invited.branch_access_scope is BranchAccessScope.SELECTED
    assert database.membership_branch_ids.get(MEMBER_ID, ()) == ()
    assert len(database.membership_audits) == 1
    accepted = await build_accept_membership_service(factory, clock(), ids(uuid4())).execute(
        TEST_BUSINESS_ID, actor=member_actor()
    )
    assert accepted.status is MembershipStatus.ACTIVE
    assert len(database.membership_audits) == 2
    assert {item.action for item in database.membership_audits.values()} == {
        MembershipAuditAction.INVITED,
        MembershipAuditAction.ACCEPTED,
    }


@pytest.mark.asyncio
async def test_duplicate_invitation_rejected_without_writes() -> None:
    database = setup_membership_database()
    with pytest.raises(MembershipAlreadyExistsError):
        await build_invite_member_service(
            InMemoryBusinessUnitOfWorkFactory(database), clock(), ids(uuid4())
        ).execute(InviteMemberCommand(TEST_BUSINESS_ID, OTHER_USER_ID), actor=owner_actor())
    assert database.commit_count == 0


@pytest.mark.asyncio
async def test_member_cannot_invite() -> None:
    database = setup_membership_database()
    with pytest.raises(BusinessPermissionDeniedError):
        await build_invite_member_service(
            InMemoryBusinessUnitOfWorkFactory(database), clock(), ids(uuid4())
        ).execute(InviteMemberCommand(TEST_BUSINESS_ID, uuid4()), actor=member_actor())


@pytest.mark.asyncio
async def test_invitation_cannot_be_accepted_by_other_user_or_twice() -> None:
    database = setup_membership_database(include_member=False)
    seed_member(database, status=MembershipStatus.INVITED)
    service = build_accept_membership_service(
        InMemoryBusinessUnitOfWorkFactory(database), clock(), ids(uuid4())
    )
    with pytest.raises(MembershipNotFoundError):
        await service.execute(FOREIGN_BUSINESS_ID, actor=member_actor())
    await service.execute(TEST_BUSINESS_ID, actor=member_actor())
    with pytest.raises(MembershipInvalidStateError):
        await service.execute(TEST_BUSINESS_ID, actor=member_actor())


@pytest.mark.asyncio
async def test_last_owner_cannot_be_demoted_or_revoked() -> None:
    database = setup_membership_database()
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    with pytest.raises(LastActiveOwnerError):
        await build_change_member_role_service(factory, clock(), ids(uuid4())).execute(
            ChangeMemberRoleCommand(TEST_BUSINESS_ID, TEST_MEMBERSHIP_ID, MembershipRole.MEMBER),
            actor=owner_actor(),
        )
    with pytest.raises(LastActiveOwnerError):
        await build_revoke_membership_service(factory, clock(), ids(uuid4())).execute(
            TEST_BUSINESS_ID, TEST_MEMBERSHIP_ID, actor=owner_actor()
        )
    assert database.commit_count == 0


@pytest.mark.asyncio
async def test_promote_member_then_demote_original_owner() -> None:
    database = setup_membership_database()
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    promoted = await build_change_member_role_service(factory, clock(), ids(uuid4())).execute(
        ChangeMemberRoleCommand(TEST_BUSINESS_ID, MEMBER_ID, MembershipRole.OWNER),
        actor=owner_actor(),
    )
    assert promoted.branch_access_scope is BranchAccessScope.ALL
    demoted = await build_change_member_role_service(factory, clock(), ids(uuid4())).execute(
        ChangeMemberRoleCommand(TEST_BUSINESS_ID, TEST_MEMBERSHIP_ID, MembershipRole.MEMBER),
        actor=owner_actor(),
    )
    assert demoted.branch_access_scope is BranchAccessScope.SELECTED
    assert database.membership_branch_ids[TEST_MEMBERSHIP_ID] == ()


@pytest.mark.asyncio
async def test_revoke_clears_access_and_reinvite_preserves_audit_history() -> None:
    database = setup_membership_database()
    database.membership_branch_ids[MEMBER_ID] = (TEST_BRANCH_ID,)
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    revoked = await build_revoke_membership_service(factory, clock(), ids(uuid4())).execute(
        TEST_BUSINESS_ID, MEMBER_ID, actor=owner_actor()
    )
    assert revoked.status is MembershipStatus.REVOKED
    assert database.membership_branch_ids[MEMBER_ID] == ()
    fresh_id = uuid4()
    await build_invite_member_service(factory, clock(), ids(fresh_id, uuid4())).execute(
        InviteMemberCommand(TEST_BUSINESS_ID, OTHER_USER_ID), actor=owner_actor()
    )
    assert len(database.memberships) == 3
    assert len(database.membership_audits) == 2


@pytest.mark.asyncio
async def test_branch_scope_selected_empty_is_deny_all() -> None:
    database = setup_membership_database()
    seed_branch(database)
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    assert (
        await build_list_branch_service(factory).execute(
            ListBranchesQuery(TEST_BUSINESS_ID), actor=member_actor()
        )
        == ()
    )
    with pytest.raises(BranchNotFoundError):
        await build_get_branch_service(factory).execute(
            TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=member_actor()
        )
    assert (
        len(
            await build_list_branch_service(factory).execute(
                ListBranchesQuery(TEST_BUSINESS_ID), actor=owner_actor()
            )
        )
        == 1
    )


@pytest.mark.asyncio
async def test_selected_branch_access_applies_to_get_and_list() -> None:
    database = setup_membership_database()
    seed_branch(database)
    seed_branch(database, branch_id=OTHER_BRANCH_ID)
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    await build_set_member_branch_access_service(factory, clock(), ids(uuid4())).execute(
        SetMemberBranchAccessCommand(
            TEST_BUSINESS_ID, MEMBER_ID, BranchAccessScope.SELECTED, (TEST_BRANCH_ID,)
        ),
        actor=owner_actor(),
    )
    found = await build_list_branch_service(factory).execute(
        ListBranchesQuery(TEST_BUSINESS_ID), actor=member_actor()
    )
    assert tuple(branch.id for branch in found) == (TEST_BRANCH_ID,)
    assert (
        await build_get_branch_service(factory).execute(
            TEST_BUSINESS_ID, TEST_BRANCH_ID, actor=member_actor()
        )
    ).id == TEST_BRANCH_ID
    with pytest.raises(BranchNotFoundError):
        await build_get_branch_service(factory).execute(
            TEST_BUSINESS_ID, OTHER_BRANCH_ID, actor=member_actor()
        )


@pytest.mark.asyncio
async def test_foreign_branch_id_fails_atomically() -> None:
    database = setup_membership_database()
    seed_branch(database)
    seed_branch(database, branch_id=OTHER_BRANCH_ID, business_id=FOREIGN_BUSINESS_ID)
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    with pytest.raises(BranchNotFoundError):
        await build_set_member_branch_access_service(factory, clock(), ids(uuid4())).execute(
            SetMemberBranchAccessCommand(
                TEST_BUSINESS_ID,
                MEMBER_ID,
                BranchAccessScope.SELECTED,
                (TEST_BRANCH_ID, OTHER_BRANCH_ID),
            ),
            actor=owner_actor(),
        )
    assert MEMBER_ID not in database.membership_branch_ids
    assert database.commit_count == 0


@pytest.mark.asyncio
async def test_all_scope_rejects_ids_and_owner_cannot_be_restricted() -> None:
    database = setup_membership_database()
    service = build_set_member_branch_access_service(
        InMemoryBusinessUnitOfWorkFactory(database), clock(), ids(uuid4())
    )
    with pytest.raises(MembershipInvalidStateError):
        await service.execute(
            SetMemberBranchAccessCommand(
                TEST_BUSINESS_ID, MEMBER_ID, BranchAccessScope.ALL, (TEST_BRANCH_ID,)
            ),
            actor=owner_actor(),
        )
    with pytest.raises(MembershipInvalidStateError):
        await service.execute(
            SetMemberBranchAccessCommand(
                TEST_BUSINESS_ID, TEST_MEMBERSHIP_ID, BranchAccessScope.SELECTED
            ),
            actor=owner_actor(),
        )


@pytest.mark.asyncio
async def test_membership_listing_owner_only_and_cross_business_target_hidden() -> None:
    database = setup_membership_database()
    factory = InMemoryBusinessUnitOfWorkFactory(database)
    listed = await build_list_memberships_service(factory).execute(
        TEST_BUSINESS_ID, actor=owner_actor()
    )
    assert len(listed) == 2
    with pytest.raises(BusinessPermissionDeniedError):
        await build_list_memberships_service(factory).execute(
            TEST_BUSINESS_ID, actor=member_actor()
        )
    with pytest.raises(MembershipNotFoundError):
        await build_revoke_membership_service(factory, clock(), ids(uuid4())).execute(
            TEST_BUSINESS_ID, uuid4(), actor=owner_actor()
        )


@pytest.mark.asyncio
async def test_failed_commit_rolls_back_membership_and_audit() -> None:
    database = setup_membership_database(include_member=False)
    factory = InMemoryBusinessUnitOfWorkFactory(database, fail_commit=True)
    with pytest.raises(RuntimeError, match="Commit failed"):
        await build_invite_member_service(factory, clock(), ids(MEMBER_ID, AUDIT_ID)).execute(
            InviteMemberCommand(TEST_BUSINESS_ID, OTHER_USER_ID), actor=owner_actor()
        )
    assert len(database.memberships) == 1
    assert database.membership_audits == {}
