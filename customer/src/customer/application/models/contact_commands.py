"""Immutable contact commands supplied with trusted host actor context."""

from dataclasses import dataclass
from uuid import UUID

from customer.application.actor import CustomerActor
from customer.domain.contact import ContactKind


@dataclass(frozen=True, slots=True)
class AddContactCommand:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID
    kind: ContactKind
    value: str
    is_primary: bool = False


@dataclass(frozen=True, slots=True)
class ContactMutationCommand:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID
    contact_id: UUID


@dataclass(frozen=True, slots=True)
class UpdateContactCommand(ContactMutationCommand):
    value: str


@dataclass(frozen=True, slots=True)
class ListContactsQuery:
    business_id: UUID
    actor: CustomerActor
    customer_id: UUID
