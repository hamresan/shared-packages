from datetime import UTC, datetime

import pytest

from business.domain import BusinessArchivedError, BusinessStatus
from tests.support.builders import TEST_BUSINESS_ID, TEST_TIME, build_business


def test_business_can_exist_without_any_branch() -> None:
    business = build_business()

    assert business.id == TEST_BUSINESS_ID
    assert business.status is BusinessStatus.ACTIVE
    assert business.archived_at is None
    assert business.created_at == TEST_TIME


def test_business_profile_update_preserves_identity_and_settings() -> None:
    business = build_business()
    changed_at = datetime(2026, 1, 2, tzinfo=UTC)

    business.update_profile(name="Updated Bakery", business_type=None, updated_at=changed_at)

    assert business.name == "Updated Bakery"
    assert business.business_type is None
    assert business.updated_at == changed_at
    assert business.id == TEST_BUSINESS_ID
    assert business.default_currency_code == "OMR"


def test_business_archive_is_non_destructive() -> None:
    business = build_business()
    changed_at = datetime(2026, 1, 2, tzinfo=UTC)

    business.archive(archived_at=changed_at)

    assert business.id == TEST_BUSINESS_ID
    assert business.status is BusinessStatus.ARCHIVED
    assert business.archived_at == changed_at
    assert business.updated_at == changed_at


def test_archived_business_rejects_profile_updates() -> None:
    business = build_business(status=BusinessStatus.ARCHIVED)

    with pytest.raises(BusinessArchivedError):
        business.update_profile(name="Not Allowed", business_type=None, updated_at=TEST_TIME)

    assert business.name == "Muscat Bakery"


def test_archived_business_cannot_be_archived_twice() -> None:
    business = build_business(status=BusinessStatus.ARCHIVED)

    with pytest.raises(BusinessArchivedError):
        business.archive(archived_at=TEST_TIME)
