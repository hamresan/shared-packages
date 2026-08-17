from store.domain import (
    Store,
    StoreAvailabilityStatus,
    StoreModerationStatus,
    StoreSetupStatus,
    StoreSuspensionReason,
)
from store.infrastructure.persistence.sqlalchemy.mappers.address import (
    StoreAddressPersistenceMapper,
)
from store.infrastructure.persistence.sqlalchemy.mappers.contacts import (
    StoreContactPersistenceMapper,
)
from store.infrastructure.persistence.sqlalchemy.mappers.currencies import (
    StoreCurrencyPersistenceMapper,
)
from store.infrastructure.persistence.sqlalchemy.mappers.datetime import UtcDateTimeMapper
from store.infrastructure.persistence.sqlalchemy.mappers.schedule import (
    WeeklyWorkingSchedulePersistenceMapper,
)
from store.infrastructure.persistence.sqlalchemy.models import StoreModel


class StorePersistenceMapper:
    def __init__(
        self,
        address_mapper: StoreAddressPersistenceMapper,
        contact_mapper: StoreContactPersistenceMapper,
        currency_mapper: StoreCurrencyPersistenceMapper,
        schedule_mapper: WeeklyWorkingSchedulePersistenceMapper,
        datetime_mapper: UtcDateTimeMapper,
    ) -> None:
        self._address_mapper = address_mapper
        self._contact_mapper = contact_mapper
        self._currency_mapper = currency_mapper
        self._schedule_mapper = schedule_mapper
        self._datetime_mapper = datetime_mapper

    def to_model(self, store: Store) -> StoreModel:
        return StoreModel(
            id=store.id,
            owner_user_id=store.owner_user_id,
            name=store.name,
            business_type=store.business_type,
            primary_language=store.primary_language,
            supported_languages=list(store.supported_languages),
            country_code=store.country_code,
            address=self._address_mapper.to_record(store.address),
            contacts=self._contact_mapper.to_records(store.contacts),
            base_currency_code=store.base_currency_code,
            currencies=self._currency_mapper.to_records(store.currencies),
            timezone=store.timezone,
            working_schedule=self._schedule_mapper.to_record(store.working_schedule),
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

    def to_domain(self, model: StoreModel) -> Store:
        created_at = self._datetime_mapper.to_domain(model.created_at)
        updated_at = self._datetime_mapper.to_domain(model.updated_at)
        if created_at is None or updated_at is None:
            raise ValueError("Persisted Store timestamps are required")
        return Store(
            id=model.id,
            owner_user_id=model.owner_user_id,
            name=model.name,
            business_type=model.business_type,
            primary_language=model.primary_language,
            supported_languages=tuple(model.supported_languages),
            country_code=model.country_code,
            address=self._address_mapper.to_domain(model.address),
            contacts=self._contact_mapper.to_domain(model.contacts),
            base_currency_code=model.base_currency_code,
            currencies=self._currency_mapper.to_domain(model.currencies),
            timezone=model.timezone,
            working_schedule=self._schedule_mapper.to_domain(model.working_schedule),
            setup_status=StoreSetupStatus(model.setup_status),
            availability_status=StoreAvailabilityStatus(model.availability_status),
            moderation_status=StoreModerationStatus(model.moderation_status),
            suspension_reason=(
                StoreSuspensionReason(model.suspension_reason)
                if model.suspension_reason is not None
                else None
            ),
            suspension_description=model.suspension_description,
            suspended_by_actor_id=model.suspended_by_actor_id,
            suspended_at=self._datetime_mapper.to_domain(model.suspended_at),
            deleted_at=self._datetime_mapper.to_domain(model.deleted_at),
            created_at=created_at,
            updated_at=updated_at,
        )
