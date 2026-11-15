from business.domain import (
    BranchAccessScope,
    BranchStatus,
    BusinessStatus,
    MembershipRole,
    MembershipStatus,
)


def test_business_and_branch_have_distinct_lifecycle_statuses() -> None:
    assert BusinessStatus.ACTIVE.value == "active"
    assert BusinessStatus.ARCHIVED.value == "archived"
    assert BranchStatus.ACTIVE.value == "active"
    assert BranchStatus.ARCHIVED.value == "archived"


def test_membership_roles_and_statuses_are_explicit() -> None:
    assert {role.value for role in MembershipRole} == {"owner", "member"}
    assert {status.value for status in MembershipStatus} == {"invited", "active", "revoked"}


def test_branch_access_distinguishes_all_from_selected() -> None:
    assert BranchAccessScope.ALL != BranchAccessScope.SELECTED
