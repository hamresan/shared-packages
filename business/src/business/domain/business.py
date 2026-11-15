from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from business.domain.enums import BusinessStatus
from business.domain.errors import BusinessArchivedError


@dataclass(slots=True)
class Business:
    id: UUID
    name: str
    business_type: str | None
    country_code: str
    default_language: str
    default_currency_code: str
    created_at: datetime
    updated_at: datetime
    status: BusinessStatus = BusinessStatus.ACTIVE
    archived_at: datetime | None = None

    def update_profile(self, *, name: str, business_type: str | None, updated_at: datetime) -> None:
        self._require_active()
        self.name = name
        self.business_type = business_type
        self.updated_at = updated_at

    def archive(self, *, archived_at: datetime) -> None:
        self._require_active()
        self.status = BusinessStatus.ARCHIVED
        self.archived_at = archived_at
        self.updated_at = archived_at

    def _require_active(self) -> None:
        if self.status is BusinessStatus.ARCHIVED:
            raise BusinessArchivedError("An archived business cannot be changed")
