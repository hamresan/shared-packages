"""Shared identity of a customer-scoped child command."""

from dataclasses import dataclass
from uuid import UUID

from customer.application.actor import CustomerActor


@dataclass(frozen=True, slots=True)
class CustomerDetailsQuery:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID


@dataclass(frozen=True, slots=True)
class CustomerChildMutation(CustomerDetailsQuery):
    child_id: UUID
