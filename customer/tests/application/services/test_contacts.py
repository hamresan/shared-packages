from uuid import uuid4

import pytest

from customer.application.models import CreateCustomerCommand, CustomerMutationCommand
from customer.application.models.contact_commands import (
    AddContactCommand,
    ContactMutationCommand,
    ListContactsQuery,
    UpdateContactCommand,
)
from customer.domain.contact import ContactKind
from customer.domain.errors import (
    CustomerInvalidStateError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerValidationError,
)
from tests.support.factories.customer_module import build_actor, build_customer_module


async def test_contact_crud_and_primary_selection_per_kind() -> None:
    module, _ = build_customer_module()
    business = uuid4()
    actor = build_actor(business)
    customer = await module.customers.create.execute(CreateCustomerCommand(business, actor))
    first = await module.contacts.add.execute(
        AddContactCommand(
            business, actor, customer.id, ContactKind.EMAIL, " ADA@Example.COM ", True
        )
    )
    assert (first.value, first.is_primary, first.is_verified) == ("ada@example.com", True, False)
    second = await module.contacts.add.execute(
        AddContactCommand(business, actor, customer.id, ContactKind.EMAIL, "b@example.com", True)
    )
    phone = await module.contacts.add.execute(
        AddContactCommand(business, actor, customer.id, ContactKind.PHONE, "+96891234567", True)
    )
    contacts = await module.contacts.list.execute(ListContactsQuery(business, actor, customer.id))
    assert len(contacts) == 3
    assert {(entry.kind, entry.is_primary) for entry in contacts} == {
        (ContactKind.EMAIL, False),
        (ContactKind.EMAIL, True),
        (ContactKind.PHONE, True),
    }
    updated = await module.contacts.update.execute(
        UpdateContactCommand(business, actor, customer.id, second.id, " NEW@example.com ")
    )
    assert (updated.value, updated.is_verified) == ("new@example.com", False)
    restored = await module.contacts.set_primary.execute(
        ContactMutationCommand(business, actor, customer.id, first.id)
    )
    assert restored.is_primary
    contacts = await module.contacts.list.execute(ListContactsQuery(business, actor, customer.id))
    assert sum(c.is_primary for c in contacts if c.kind == ContactKind.EMAIL) == 1
    assert next(c for c in contacts if c.id == phone.id).is_primary
    await module.contacts.remove.execute(
        ContactMutationCommand(business, actor, customer.id, second.id)
    )
    remaining = await module.contacts.list.execute(ListContactsQuery(business, actor, customer.id))
    assert len(remaining) == 2


@pytest.mark.parametrize(
    "kind,value",
    [
        (ContactKind.EMAIL, "not-an-email"),
        (ContactKind.EMAIL, "a@"),
        (ContactKind.EMAIL, "a" * 255 + "@example.com"),
        (ContactKind.PHONE, "91234567"),
        (ContactKind.PHONE, "+000000000"),
    ],
)
async def test_invalid_contacts_are_rejected(kind: ContactKind, value: str) -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    with pytest.raises(CustomerValidationError):
        await module.contacts.add.execute(
            AddContactCommand(actor.business_id, actor, customer.id, kind, value)
        )


async def test_contact_ownership_and_archive_are_enforced() -> None:
    module, _ = build_customer_module()
    owner = build_actor(uuid4())
    foreign = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(owner.business_id, owner)
    )
    contact = await module.contacts.add.execute(
        AddContactCommand(owner.business_id, owner, customer.id, ContactKind.EMAIL, "x@y.com")
    )
    with pytest.raises(CustomerNotFoundError):
        await module.contacts.list.execute(
            ListContactsQuery(foreign.business_id, foreign, customer.id)
        )
    with pytest.raises(CustomerPermissionDeniedError):
        await module.contacts.list.execute(
            ListContactsQuery(owner.business_id, foreign, customer.id)
        )
    with pytest.raises(CustomerNotFoundError):
        await module.contacts.remove.execute(
            ContactMutationCommand(owner.business_id, owner, customer.id, uuid4())
        )
    other_customer = await module.customers.create.execute(
        CreateCustomerCommand(owner.business_id, owner)
    )
    with pytest.raises(CustomerNotFoundError):
        await module.contacts.set_primary.execute(
            ContactMutationCommand(owner.business_id, owner, other_customer.id, contact.id)
        )
    await module.customers.archive.execute(
        CustomerMutationCommand(owner.business_id, owner, customer.id, 1)
    )
    with pytest.raises(CustomerInvalidStateError):
        await module.contacts.add.execute(
            AddContactCommand(owner.business_id, owner, customer.id, ContactKind.EMAIL, "z@y.com")
        )
