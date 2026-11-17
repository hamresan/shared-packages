"""Queries and paginated search results."""

from dataclasses import dataclass
from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.models.customer_result import CustomerResult


@dataclass(frozen=True, slots=True)
class GetCustomerQuery:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID


@dataclass(frozen=True, slots=True)
class CustomerSearchQuery:
    business_id: UUID
    actor: CustomerActor
    name_contains: str | None = None
    offset: int = 0
    limit: int = 20


@dataclass(frozen=True, slots=True)
class CustomerSearchResult:
    items: tuple[CustomerResult, ...]
    has_more: bool
