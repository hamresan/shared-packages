"""Commands for Customer aggregate mutations."""

from dataclasses import dataclass
from uuid import UUID

from customer.application.actor import CustomerActor


@dataclass(frozen=True, slots=True)
class CreateCustomerCommand:
    business_id: UUID
    actor: CustomerActor
    display_name: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateCustomerCommand:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID
    expected_version: int
    display_name: str | None


@dataclass(frozen=True, slots=True)
class CustomerMutationCommand:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID
    expected_version: int
