from dataclasses import dataclass
from uuid import UUID

from business.domain.value_objects import BranchAddress, BranchContact


@dataclass(frozen=True, slots=True)
class CreateBusinessCommand:
    name: str
    country_code: str
    default_language: str
    default_currency_code: str
    business_type: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateBusinessCommand:
    business_id: UUID
    name: str
    business_type: str | None


@dataclass(frozen=True, slots=True)
class CreateBranchCommand:
    business_id: UUID
    name: str
    timezone: str
    address: BranchAddress | None = None
    contact: BranchContact | None = None


@dataclass(frozen=True, slots=True)
class UpdateBranchCommand:
    business_id: UUID
    branch_id: UUID
    name: str
    timezone: str
    address: BranchAddress | None
    contact: BranchContact | None


@dataclass(frozen=True, slots=True)
class ListBranchesQuery:
    business_id: UUID
    city: str | None = None
    country_code: str | None = None
