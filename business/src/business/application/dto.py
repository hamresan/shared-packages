from dataclasses import dataclass
from uuid import UUID


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
