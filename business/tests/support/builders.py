from datetime import UTC, datetime
from uuid import UUID

from business.application.dto import CreateBusinessCommand
from business.domain import Business, BusinessMembership, BusinessStatus, MembershipRole
from business.domain.enums import MembershipStatus

TEST_TIME = datetime(2026, 1, 1, tzinfo=UTC)
TEST_BUSINESS_ID = UUID("b45f0f68-3c8f-4fb1-b5e4-3e10bcdb7efe")
TEST_USER_ID = UUID("ddc43236-d4b7-495c-a09d-3e15ddca5d82")
OTHER_USER_ID = UUID("bc4187f0-cdb6-407a-88a3-cd30bcf3a9d6")
TEST_MEMBERSHIP_ID = UUID("a1361ec5-7da9-4475-95c6-75e9d069d312")


def build_create_command(name: str = "My Business") -> CreateBusinessCommand:
    return CreateBusinessCommand(
        name=name,
        country_code="om",
        default_language="en",
        default_currency_code="omr",
    )


def build_business(
    *,
    business_id: UUID = TEST_BUSINESS_ID,
    name: str = "Muscat Bakery",
    status: BusinessStatus = BusinessStatus.ACTIVE,
) -> Business:
    return Business(
        id=business_id,
        name=name,
        business_type="bakery",
        country_code="OM",
        default_language="en",
        default_currency_code="OMR",
        created_at=TEST_TIME,
        updated_at=TEST_TIME,
        status=status,
        archived_at=TEST_TIME if status is BusinessStatus.ARCHIVED else None,
    )


def build_membership(
    *,
    membership_id: UUID = TEST_MEMBERSHIP_ID,
    business_id: UUID = TEST_BUSINESS_ID,
    user_id: UUID = TEST_USER_ID,
    role: MembershipRole = MembershipRole.OWNER,
    status: MembershipStatus = MembershipStatus.ACTIVE,
) -> BusinessMembership:
    return BusinessMembership(
        id=membership_id,
        business_id=business_id,
        user_id=user_id,
        role=role,
        status=status,
        created_at=TEST_TIME,
        updated_at=TEST_TIME,
    )
