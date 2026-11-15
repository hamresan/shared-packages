from uuid import UUID

from business.domain import Business, BusinessStatus
from business.domain.branch import Branch
from business.domain.enums import BranchStatus, MembershipRole
from business.domain.value_objects import BranchAddress, BranchContact
from tests.support.builders import (
    TEST_BRANCH_ID,
    TEST_BUSINESS_ID,
    TEST_MEMBERSHIP_ID,
    TEST_USER_ID,
    build_branch,
    build_business,
    build_membership,
)
from tests.support.fakes.database import InMemoryBusinessDatabase


def seed_owned_business(
    database: InMemoryBusinessDatabase,
    *,
    business_id: UUID = TEST_BUSINESS_ID,
    user_id: UUID = TEST_USER_ID,
    membership_id: UUID = TEST_MEMBERSHIP_ID,
    status: BusinessStatus = BusinessStatus.ACTIVE,
) -> Business:
    business = build_business(business_id=business_id, status=status)
    membership = build_membership(
        membership_id=membership_id,
        business_id=business_id,
        user_id=user_id,
        role=MembershipRole.OWNER,
    )
    database.businesses[business.id] = business
    database.memberships[membership.id] = membership
    return business


def seed_branch(
    database: InMemoryBusinessDatabase,
    *,
    branch_id: UUID = TEST_BRANCH_ID,
    business_id: UUID = TEST_BUSINESS_ID,
    address: BranchAddress | None = None,
    contact: BranchContact | None = None,
    status: BranchStatus = BranchStatus.ACTIVE,
) -> Branch:
    branch = build_branch(
        branch_id=branch_id,
        business_id=business_id,
        status=status,
        address=address,
        contact=contact,
    )
    database.branches[branch.id] = branch
    return branch
