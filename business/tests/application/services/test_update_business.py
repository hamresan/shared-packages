from datetime import UTC, datetime
from uuid import UUID

import pytest

from business.application import AuthenticatedActor, UpdateBusinessCommand
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
from tests.support.factories import build_update_service
from tests.support.fakes import (
    FixedClock,
    InMemoryBusinessDatabase,
    InMemoryBusinessUnitOfWorkFactory,
)


async def test_owner_updates_business_profile_without_changing_identity() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner
    changed_at = datetime(2026, 1, 3, tzinfo=UTC)
    service = build_update_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(changed_at)
    )

    updated = await service.execute(
        UpdateBusinessCommand(TEST_BUSINESS_ID, "  New Name  ", " SALON "),
        actor=AuthenticatedActor(TEST_USER_ID),
    )

    assert updated.name == database.businesses[TEST_BUSINESS_ID].name == "New Name"
    assert updated.business_type == "salon"
    assert updated.updated_at == changed_at
    assert updated.created_at == TEST_TIME
    assert updated.id == TEST_BUSINESS_ID
    assert len(database.memberships) == 1
    assert database.commit_count == 1


async def test_active_member_cannot_update_business() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    member = build_membership(
        membership_id=UUID(int=20), user_id=OTHER_USER_ID, role=MembershipRole.MEMBER
    )
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner
    database.memberships[member.id] = member
    service = build_update_service(
        InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
    )

    with pytest.raises(BusinessPermissionDeniedError):
        await service.execute(
            UpdateBusinessCommand(TEST_BUSINESS_ID, "Intruder", None),
            actor=AuthenticatedActor(OTHER_USER_ID),
        )

    assert database.businesses[TEST_BUSINESS_ID].name == "Muscat Bakery"
    assert database.commit_count == 0


async def test_outsider_cannot_update_business() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    with pytest.raises(BusinessNotFoundError):
        await build_update_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBusinessCommand(TEST_BUSINESS_ID, "Not Allowed", None),
            actor=AuthenticatedActor(OTHER_USER_ID),
        )

    assert database.commit_count == 0


async def test_update_rejects_invalid_business_profile_without_writing() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    with pytest.raises(ValueError):
        await build_update_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBusinessCommand(TEST_BUSINESS_ID, " ", None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.businesses[TEST_BUSINESS_ID].name == "Muscat Bakery"
    assert database.commit_count == 0


async def test_archived_business_cannot_be_updated() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business(status=BusinessStatus.ARCHIVED)
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner

    with pytest.raises(BusinessArchivedError):
        await build_update_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBusinessCommand(TEST_BUSINESS_ID, "Forbidden", None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.commit_count == 0


async def test_commit_failure_does_not_leak_unsaved_update() -> None:
    database = InMemoryBusinessDatabase()
    business = build_business()
    owner = build_membership()
    database.businesses[business.id] = business
    database.memberships[owner.id] = owner
    service = build_update_service(
        InMemoryBusinessUnitOfWorkFactory(database, fail_commit=True), FixedClock(TEST_TIME)
    )

    with pytest.raises(RuntimeError, match="Commit failed"):
        await service.execute(
            UpdateBusinessCommand(TEST_BUSINESS_ID, "No Change", None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )

    assert database.businesses[TEST_BUSINESS_ID].name == "Muscat Bakery"
    assert database.commit_count == 0


async def test_update_handles_orphaned_membership_without_exposing_data() -> None:
    database = InMemoryBusinessDatabase()
    membership = build_membership()
    database.memberships[membership.id] = membership

    with pytest.raises(BusinessNotFoundError):
        await build_update_service(
            InMemoryBusinessUnitOfWorkFactory(database), FixedClock(TEST_TIME)
        ).execute(
            UpdateBusinessCommand(TEST_BUSINESS_ID, "Missing", None),
            actor=AuthenticatedActor(TEST_USER_ID),
        )
