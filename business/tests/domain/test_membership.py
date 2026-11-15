from business.domain import MembershipRole, MembershipStatus
from tests.support.builders import TEST_BUSINESS_ID, TEST_USER_ID, build_membership


def test_owner_membership_references_an_external_identity() -> None:
    membership = build_membership()

    assert membership.business_id == TEST_BUSINESS_ID
    assert membership.user_id == TEST_USER_ID
    assert membership.role is MembershipRole.OWNER
    assert membership.status is MembershipStatus.ACTIVE
