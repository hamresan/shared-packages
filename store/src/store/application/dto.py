from dataclasses import dataclass
from uuid import UUID

from store.domain import Store


@dataclass(frozen=True, slots=True)
class CreateStoreCommand:
    owner_user_id: UUID
    name: str
    business_type: str
    primary_language: str
    country_code: str
    base_currency_code: str


@dataclass(frozen=True, slots=True)
class CreateStoreResult:
    store: Store


@dataclass(frozen=True, slots=True)
class GetStoreQuery:
    store_id: UUID


@dataclass(frozen=True, slots=True)
class GetOwnedStoreQuery:
    owner_user_id: UUID
