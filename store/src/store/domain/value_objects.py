from dataclasses import dataclass
from decimal import Decimal

from store.domain.enums import StoreContactType


@dataclass(frozen=True, slots=True)
class StoreAddress:
    state_or_province: str | None = None
    city: str | None = None
    area: str | None = None
    street: str | None = None
    building: str | None = None
    postal_code: str | None = None
    additional_details: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


@dataclass(frozen=True, slots=True)
class StoreContact:
    type: StoreContactType
    value: str
    label: str | None = None
    is_primary: bool = False


@dataclass(frozen=True, slots=True)
class StoreCurrency:
    code: str
    exchange_rate: Decimal


@dataclass(frozen=True, slots=True)
class DailyWorkingHours:
    opens_at: str
    closes_at: str


@dataclass(frozen=True, slots=True)
class WeeklyWorkingSchedule:
    monday: DailyWorkingHours | None = None
    tuesday: DailyWorkingHours | None = None
    wednesday: DailyWorkingHours | None = None
    thursday: DailyWorkingHours | None = None
    friday: DailyWorkingHours | None = None
    saturday: DailyWorkingHours | None = None
    sunday: DailyWorkingHours | None = None
