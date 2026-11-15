from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from business.domain.enums import BranchStatus
from business.domain.errors import BranchAlreadyActiveError, BranchArchivedError
from business.domain.value_objects import BranchAddress, BranchContact


@dataclass(slots=True)
class Branch:
    id: UUID
    business_id: UUID
    name: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    address: BranchAddress | None = None
    contact: BranchContact | None = None
    status: BranchStatus = BranchStatus.ACTIVE
    archived_at: datetime | None = None

    def update_details(
        self,
        *,
        name: str,
        timezone: str,
        address: BranchAddress | None,
        contact: BranchContact | None,
        updated_at: datetime,
    ) -> None:
        if self.status is BranchStatus.ARCHIVED:
            raise BranchArchivedError("An archived branch cannot be modified")
        self.name = name
        self.timezone = timezone
        self.address = address
        self.contact = contact
        self.updated_at = updated_at

    def archive(self, *, archived_at: datetime) -> None:
        if self.status is BranchStatus.ARCHIVED:
            raise BranchArchivedError("Branch is already archived")
        self.status = BranchStatus.ARCHIVED
        self.archived_at = archived_at
        self.updated_at = archived_at

    def reactivate(self, *, reactivated_at: datetime) -> None:
        if self.status is BranchStatus.ACTIVE:
            raise BranchAlreadyActiveError("Branch is already active")
        self.status = BranchStatus.ACTIVE
        self.archived_at = None
        self.updated_at = reactivated_at
