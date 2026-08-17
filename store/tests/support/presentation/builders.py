from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from store.domain import (
    DailyWorkingHours,
    Store,
    StoreAddress,
    StoreContact,
    StoreContactType,
    StoreCurrency,
    WeeklyWorkingSchedule,
)


class StorePresentationBuilder:
    def __init__(self) -> None:
        self.store_id = uuid4()
        self.owner_user_id = uuid4()

    def build(self) -> Store:
        now = datetime(2026, 8, 17, 8, 0, tzinfo=UTC)
        return Store(
            id=self.store_id,
            owner_user_id=self.owner_user_id,
            name="Demo Store",
            business_type="retail",
            primary_language="en",
            supported_languages=("en", "ar"),
            country_code="OM",
            address=StoreAddress(city="Muscat", latitude=Decimal("23.5880")),
            contacts=(
                StoreContact(
                    type=StoreContactType.WHATSAPP,
                    value="+96890000000",
                    is_primary=True,
                ),
            ),
            base_currency_code="OMR",
            currencies=(StoreCurrency(code="OMR", exchange_rate=Decimal("1")),),
            timezone="Asia/Muscat",
            working_schedule=WeeklyWorkingSchedule(
                monday=DailyWorkingHours(opens_at="09:00", closes_at="18:00")
            ),
            created_at=now,
            updated_at=now,
        )
