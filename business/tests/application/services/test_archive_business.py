from datetime import UTC, datetime
from uuid import UUID

import pytest

from business.application import AuthenticatedActor
from business.domain import (
    BusinessArchivedError,
    BusinessNotFoundError,
    BusinessPermissionDeniedError,
    BusinessStatus,
    MembershipRole,
)
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_BUSINESS_ID,
    TEST_TIME,
    TEST_USER_ID,
    build_business,
    build_membership,
)
from tests.support.factories import build_archive_service, build_get_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
)


async def test_owner_archives_business_but_preserves_membership_and_readability() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    membership = build_membership()
    database.businesses[business.id] = business
    database.memberships[membership.id] = membership
    uow_factory = InMemoryBusinessUnitOfWorkFactory(database)
    changed_at = datetime(2026, 2, 1, tzinfo=UTC)

    archived = await build_archive_service(uow_factory, FixedClock(changed_at)).execute(
        business.id, actor=AuthenticatedActor(TEST_USER_ID)
    )

    assert archived.status is BusinessStatus.ARCHIVED
    assert archived.archived_at == changed_at
    assert database.businesses[business.id].status is BusinessStatus.ARCHIVED
    assert database.businesses[business.id].id == TEST_BUSINESS_ID
    assert len(database.memberships) == 1
    assert database.commit_count == 1
    loaded = await build_get_service(uow_factory).execute(
        business.id, actor=AuthenticatedActor(TEST_USER_ID)
    )
    assert loaded.id == business.id


async def test_archiving_twice_fails_without_an_extra_commit() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business(status=BusinessStatus.ARCHIVED)
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    with pytest.raises(BusinessArchivedError):
        await build_archive_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, actor=AuthenticatedActor(TEST_USER_ID))

    assert database.commit_count == 0


async def test_non_owner_member_cannot_archive_business() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    member = build_membership(
        membership_id=UUID(int=20), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner
    database.memberships[member.id] = member

    with pytest.raises(BusinessPermissionDeniedError):
        await build_archive_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, actor=AuthenticatedActor(OTHER_USER_ID))

    assert database.businesses[TEST_BUSINESS_ID].status is BusinessStatus.ACTIVE
    assert database.commit_count == 0


async def test_outsider_cannot_archive_business() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    with pytest.raises(BusinessNotFoundError):
        await build_archive_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, actor=AuthenticatedActor(OTHER_USER_ID))

    assert database.commit_count == 0


async def test_archive_rejects_orphaned_membership() -> None:
    database = InMemoryBusinessDatabase()
    owner = build_membership()
    database.memberships[owner.id] = owner

    with pytest.raises(BusinessNotFoundError):
        await build_archive_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(TEST_BUSINESS_ID, actor=AuthenticatedActor(TEST_USER_ID))
