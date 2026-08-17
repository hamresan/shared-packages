from store.domain import (
    DailyWorkingHours,
    Store,
    StoreAddress,
    StoreContact,
    StoreCurrency,
    WeeklyWorkingSchedule,
)
from store.presentation.schemas import (
    DailyWorkingHoursResponse,
    StoreAddressResponse,
    StoreContactResponse,
    StoreCurrencyResponse,
    StoreResponse,
    WeeklyWorkingScheduleResponse,
)


class StoreValueObjectResponseMapper:
    def to_address(self, address: StoreAddress | None) -> StoreAddressResponse | None:
        if address is None:
            return None
        return StoreAddressResponse(
            state_or_province=address.state_or_province,
            city=address.city,
            area=address.area,
            street=address.street,
            building=address.building,
            postal_code=address.postal_code,
            additional_details=address.additional_details,
            latitude=address.latitude,
            longitude=address.longitude,
        )

    def to_contact(self, contact: StoreContact) -> StoreContactResponse:
        return StoreContactResponse(
            type=contact.type.value,
            value=contact.value,
            label=contact.label,
            is_primary=contact.is_primary,
        )

    def to_currency(self, currency: StoreCurrency) -> StoreCurrencyResponse:
        return StoreCurrencyResponse(
            code=currency.code,
            exchange_rate=currency.exchange_rate,
        )

    def to_working_hours(
        self,
        hours: DailyWorkingHours | None,
    ) -> DailyWorkingHoursResponse | None:
        if hours is None:
            return None
        return DailyWorkingHoursResponse(opens_at=hours.opens_at, closes_at=hours.closes_at)

    def to_working_schedule(
        self,
        schedule: WeeklyWorkingSchedule | None,
    ) -> WeeklyWorkingScheduleResponse | None:
        if schedule is None:
            return None
        return WeeklyWorkingScheduleResponse(
            monday=self.to_working_hours(schedule.monday),
            tuesday=self.to_working_hours(schedule.tuesday),
            wednesday=self.to_working_hours(schedule.wednesday),
            thursday=self.to_working_hours(schedule.thursday),
            friday=self.to_working_hours(schedule.friday),
            saturday=self.to_working_hours(schedule.saturday),
            sunday=self.to_working_hours(schedule.sunday),
        )


class StoreResponseMapper:
    def __init__(self, value_object_mapper: StoreValueObjectResponseMapper) -> None:
        self._value_object_mapper = value_object_mapper

    def to_response(self, store: Store) -> StoreResponse:
        return StoreResponse(
            id=store.id,
            owner_user_id=store.owner_user_id,
            name=store.name,
            business_type=store.business_type,
            primary_language=store.primary_language,
            supported_languages=list(store.supported_languages),
            country_code=store.country_code,
            address=self._value_object_mapper.to_address(store.address),
            contacts=[self._value_object_mapper.to_contact(item) for item in store.contacts],
            base_currency_code=store.base_currency_code,
            currencies=[self._value_object_mapper.to_currency(item) for item in store.currencies],
            timezone=store.timezone,
            working_schedule=self._value_object_mapper.to_working_schedule(
                store.working_schedule
            ),
            setup_status=store.setup_status.value,
            availability_status=store.availability_status.value,
            moderation_status=store.moderation_status.value,
            suspension_reason=(
                store.suspension_reason.value if store.suspension_reason is not None else None
            ),
            suspension_description=store.suspension_description,
            suspended_by_actor_id=store.suspended_by_actor_id,
            suspended_at=store.suspended_at,
            deleted_at=store.deleted_at,
            created_at=store.created_at,
            updated_at=store.updated_at,
        )
