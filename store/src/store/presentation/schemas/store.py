from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateStoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    business_type: str
    primary_language: str
    country_code: str
    base_currency_code: str


class StoreAddressResponse(BaseModel):
    state_or_province: str | None = None
    city: str | None = None
    area: str | None = None
    street: str | None = None
    building: str | None = None
    postal_code: str | None = None
    additional_details: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class StoreContactResponse(BaseModel):
    type: str
    value: str
    label: str | None = None
    is_primary: bool = False


class StoreCurrencyResponse(BaseModel):
    code: str
    exchange_rate: Decimal


class DailyWorkingHoursResponse(BaseModel):
    opens_at: str
    closes_at: str


class WeeklyWorkingScheduleResponse(BaseModel):
    monday: DailyWorkingHoursResponse | None = None
    tuesday: DailyWorkingHoursResponse | None = None
    wednesday: DailyWorkingHoursResponse | None = None
    thursday: DailyWorkingHoursResponse | None = None
    friday: DailyWorkingHoursResponse | None = None
    saturday: DailyWorkingHoursResponse | None = None
    sunday: DailyWorkingHoursResponse | None = None


class StoreResponse(BaseModel):
    id: UUID
    owner_user_id: UUID
    name: str
    business_type: str
    primary_language: str
    supported_languages: list[str]
    country_code: str
    address: StoreAddressResponse | None
    contacts: list[StoreContactResponse]
    base_currency_code: str
    currencies: list[StoreCurrencyResponse]
    timezone: str | None
    working_schedule: WeeklyWorkingScheduleResponse | None
    setup_status: str
    availability_status: str
    moderation_status: str
    suspension_reason: str | None
    suspension_description: str | None
    suspended_by_actor_id: str | None
    suspended_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
