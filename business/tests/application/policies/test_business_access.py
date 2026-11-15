import pytest

from business.application.policies import BusinessAccessPolicy
from business.domain import (
    BusinessNotFoundError,
    BusinessPermissionDeniedError,
    MembershipRole,
    MembershipStatus,
)
from tests.support.builders import build_membership


def test_owner_membership_can_access_and_modify_business() -> None:
    policy = BusinessAccessPolicy()
    owner = build_membership()

    assert policy.require_member(owner) is owner
    policy.require_owner(owner)


def test_active_non_owner_member_cannot_perform_owner_operations() -> None:
    policy = BusinessAccessPolicy()
    member = build_membership(role=MembershipRole.MEMBER)

    assert policy.require_member(member) is member
    with pytest.raises(BusinessPermissionDeniedError):
        policy.require_owner(member)


@pytest.mark.parametrize("status", [MembershipStatus.INVITED, MembershipStatus.REVOKED])
def test_inactive_membership_cannot_access_business(status: MembershipStatus) -> None:
    policy = BusinessAccessPolicy()
    membership = build_membership(status=status)

    with pytest.raises(BusinessNotFoundError):
        policy.require_member(membership)
    with pytest.raises(BusinessNotFoundError):
        policy.require_owner(membership)


def test_missing_membership_is_not_visible() -> None:
    policy = BusinessAccessPolicy()

    with pytest.raises(BusinessNotFoundError):
        policy.require_member(None)
    with pytest.raises(BusinessNotFoundError):
        policy.require_owner(None)
