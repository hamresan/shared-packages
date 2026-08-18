from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from store.domain import (
    DailyWorkingHours,
    Store,
    StoreAddress,
    StoreAvailabilityStatus,
    StoreContact,
    StoreContactType,
    StoreCurrency,
    StoreModerationStatus,
    StoreSetupStatus,
    StoreSuspensionReason,
    WeeklyWorkingSchedule,
)


def build_persistence_store() -> Store:
    now = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
    return Store(
        id=uuid4(),
        owner_user_id=uuid4(),
        name="Persistence Store",
        business_type="retail",
        primary_language="en",
        supported_languages=("en", "ar"),
        country_code="OM",
        address=StoreAddress(
            city="Muscat",
            latitude=Decimal("23.5880"),
            longitude=Decimal("58.3829"),
        ),
        contacts=(
            StoreContact(
                type=StoreContactType.WHATSAPP,
                value="+96890000000",
                is_primary=True,
            ),
        ),
        base_currency_code="OMR",
        currencies=(
            StoreCurrency(code="OMR", exchange_rate=Decimal("1")),
            StoreCurrency(code="USD", exchange_rate=Decimal("0.3845")),
        ),
        timezone="Asia/Muscat",
        working_schedule=WeeklyWorkingSchedule(
            sunday=DailyWorkingHours(opens_at="09:00", closes_at="18:00")
        ),
        setup_status=StoreSetupStatus.READY,
        availability_status=StoreAvailabilityStatus.ONLINE,
        moderation_status=StoreModerationStatus.SUSPENDED,
        suspension_reason=StoreSuspensionReason.POLICY_VIOLATION,
        suspension_description="Policy review",
        suspended_by_actor_id="admin-1",
        suspended_at=now,
        created_at=now,
        updated_at=now,
    )
