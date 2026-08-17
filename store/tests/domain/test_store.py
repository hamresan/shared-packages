from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from store.domain import (
    Store,
    StoreAvailabilityStatus,
    StoreModerationStatus,
    StoreSuspensionReason,
)


def build_store() -> Store:
    now = datetime(2026, 8, 16, tzinfo=UTC)
    return Store(
        id=uuid4(),
        owner_user_id=uuid4(),
        name="Store",
        business_type="retail",
        primary_language="en",
        country_code="OM",
        base_currency_code="OMR",
        created_at=now,
        updated_at=now,
        supported_languages=("en",),
    )


def test_store_changes_availability() -> None:
    store = build_store()
    changed_at = store.updated_at + timedelta(minutes=1)

    store.change_availability(StoreAvailabilityStatus.ONLINE, updated_at=changed_at)

    assert store.availability_status is StoreAvailabilityStatus.ONLINE
    assert store.updated_at == changed_at


def test_store_requires_description_for_other_suspension_reason() -> None:
    store = build_store()

    with pytest.raises(ValueError):
        store.suspend(
            reason=StoreSuspensionReason.OTHER,
            description=None,
            actor_id="admin",
            suspended_at=store.updated_at,
        )


def test_store_can_suspend_and_unsuspend() -> None:
    store = build_store()
    suspended_at = store.updated_at + timedelta(minutes=1)

    store.suspend(
        reason=StoreSuspensionReason.POLICY_VIOLATION,
        description=None,
        actor_id="admin-1",
        suspended_at=suspended_at,
    )

    assert store.moderation_status is StoreModerationStatus.SUSPENDED
    assert store.suspended_by_actor_id == "admin-1"

    restored_at = suspended_at + timedelta(minutes=1)
    store.unsuspend(updated_at=restored_at)

    assert store.moderation_status is StoreModerationStatus.ACTIVE
    assert store.suspension_reason is None
    assert store.suspended_by_actor_id is None
    assert store.updated_at == restored_at
