from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from store.domain.enums import (
    StoreAvailabilityStatus,
    StoreModerationStatus,
    StoreSetupStatus,
    StoreSuspensionReason,
)
from store.domain.value_objects import (
    StoreAddress,
    StoreContact,
    StoreCurrency,
    WeeklyWorkingSchedule,
)


@dataclass(slots=True)
class Store:
    id: UUID
    owner_user_id: UUID
    name: str
    business_type: str
    primary_language: str
    country_code: str
    base_currency_code: str
    created_at: datetime
    updated_at: datetime
    supported_languages: tuple[str, ...] = field(default_factory=tuple)
    address: StoreAddress | None = None
    contacts: tuple[StoreContact, ...] = field(default_factory=tuple)
    currencies: tuple[StoreCurrency, ...] = field(default_factory=tuple)
    timezone: str | None = None
    working_schedule: WeeklyWorkingSchedule | None = None
    setup_status: StoreSetupStatus = StoreSetupStatus.DRAFT
    availability_status: StoreAvailabilityStatus = StoreAvailabilityStatus.OFFLINE
    moderation_status: StoreModerationStatus = StoreModerationStatus.ACTIVE
    suspension_reason: StoreSuspensionReason | None = None
    suspension_description: str | None = None
    suspended_by_actor_id: str | None = None
    suspended_at: datetime | None = None
    deleted_at: datetime | None = None

    def update_profile(self, *, name: str, business_type: str, updated_at: datetime) -> None:
        self.name = name
        self.business_type = business_type
        self.updated_at = updated_at

    def update_languages(
        self,
        *,
        primary_language: str,
        supported_languages: tuple[str, ...],
        updated_at: datetime,
    ) -> None:
        self.primary_language = primary_language
        self.supported_languages = supported_languages
        self.updated_at = updated_at

    def change_availability(
        self,
        status: StoreAvailabilityStatus,
        *,
        updated_at: datetime,
    ) -> None:
        self.availability_status = status
        self.updated_at = updated_at

    def suspend(
        self,
        *,
        reason: StoreSuspensionReason,
        description: str | None,
        actor_id: str,
        suspended_at: datetime,
    ) -> None:
        if reason is StoreSuspensionReason.OTHER and not description:
            raise ValueError("Suspension description is required when reason is other")
        self.moderation_status = StoreModerationStatus.SUSPENDED
        self.suspension_reason = reason
        self.suspension_description = description
        self.suspended_by_actor_id = actor_id
        self.suspended_at = suspended_at
        self.updated_at = suspended_at

    def unsuspend(self, *, updated_at: datetime) -> None:
        self.moderation_status = StoreModerationStatus.ACTIVE
        self.suspension_reason = None
        self.suspension_description = None
        self.suspended_by_actor_id = None
        self.suspended_at = None
        self.updated_at = updated_at
