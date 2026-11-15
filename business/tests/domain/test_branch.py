from datetime import UTC, datetime

import pytest

from business.domain import (
    BranchAddress,
    BranchAlreadyActiveError,
    BranchArchivedError,
    BranchContact,
    BranchStatus,
)
from tests.support.builders import TEST_BRANCH_ID, TEST_BUSINESS_ID, TEST_TIME, build_branch


def test_branch_is_associated_with_one_business_and_needs_no_address() -> None:
    branch = build_branch()

    assert branch.id == TEST_BRANCH_ID
    assert branch.business_id == TEST_BUSINESS_ID
    assert branch.address is None
    assert branch.contact is None
    assert branch.status is BranchStatus.ACTIVE


def test_update_branch_details_preserves_association_and_identity() -> None:
    branch = build_branch()
    updated_at = datetime(2026, 1, 2, tzinfo=UTC)
    address = BranchAddress(city="Muscat")
    contact = BranchContact(phone="+96812345678")

    branch.update_details(
        name="Updated",
        timezone="Asia/Dubai",
        address=address,
        contact=contact,
        updated_at=updated_at,
    )

    assert branch.id == TEST_BRANCH_ID
    assert branch.business_id == TEST_BUSINESS_ID
    assert branch.name == "Updated"
    assert branch.timezone == "Asia/Dubai"
    assert branch.address == address
    assert branch.contact == contact
    assert branch.updated_at == updated_at


def test_archiving_and_reactivating_branch_preserves_historic_identity() -> None:
    branch = build_branch()
    archived_at = datetime(2026, 1, 2, tzinfo=UTC)
    reactivated_at = datetime(2026, 1, 3, tzinfo=UTC)

    branch.archive(archived_at=archived_at)

    assert branch.id == TEST_BRANCH_ID
    assert branch.status is BranchStatus.ARCHIVED
    assert branch.archived_at == archived_at
    assert branch.updated_at == archived_at

    branch.reactivate(reactivated_at=reactivated_at)

    assert branch.id == TEST_BRANCH_ID
    assert branch.business_id == TEST_BUSINESS_ID
    assert branch.status is BranchStatus.ACTIVE
    assert branch.archived_at is None
    assert branch.updated_at == reactivated_at


def test_cannot_update_archived_branch() -> None:
    branch = build_branch(status=BranchStatus.ARCHIVED)

    with pytest.raises(BranchArchivedError):
        branch.update_details(
            name="Forbidden", timezone="UTC", address=None, contact=None, updated_at=TEST_TIME
        )

    assert branch.name == "Main Branch"


def test_cannot_archive_branch_twice() -> None:
    branch = build_branch(status=BranchStatus.ARCHIVED)

    with pytest.raises(BranchArchivedError):
        branch.archive(archived_at=TEST_TIME)


def test_cannot_reactivate_active_branch() -> None:
    branch = build_branch()

    with pytest.raises(BranchAlreadyActiveError):
        branch.reactivate(reactivated_at=TEST_TIME)
