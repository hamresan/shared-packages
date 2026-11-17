from uuid import uuid4

import pytest

from customer.application.models import CreateCustomerCommand
from customer.application.models.address_commands import AddAddressCommand, UpdateAddressCommand
from customer.application.models.profile_detail_commands import (
    CustomerChildMutation,
    CustomerDetailsQuery,
)
from customer.domain.errors import CustomerNotFoundError, CustomerValidationError
from tests.support.factories.customer_module import build_actor, build_customer_module


async def test_address_lifecycle_default_is_unique_and_scoped() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    owner = await module.customers.create.execute(CreateCustomerCommand(actor.business_id, actor))
    first = await module.addresses.add.execute(
        AddAddressCommand(
            actor.business_id, actor, owner.id, "Home", "om", "Street 1", "Muscat", is_default=True
        )
    )
    second = await module.addresses.add.execute(
        AddAddressCommand(
            actor.business_id, actor, owner.id, "Office", "OM", "Street 2", "Sohar", is_default=True
        )
    )
    items = await module.addresses.list.execute(
        CustomerDetailsQuery(actor.business_id, actor, owner.id)
    )
    assert sum(item.is_default for item in items) == 1
    assert {item.country_code for item in items} == {"OM"}
    updated = await module.addresses.update.execute(
        UpdateAddressCommand(
            actor.business_id, actor, owner.id, second.id, "Work", "AE", "Road", "Dubai"
        )
    )
    assert updated.country_code == "AE"
    restored = await module.addresses.set_default.execute(
        CustomerChildMutation(actor.business_id, actor, owner.id, first.id)
    )
    assert restored.is_default
    await module.addresses.remove.execute(
        CustomerChildMutation(actor.business_id, actor, owner.id, second.id)
    )
    assert (
        len(
            await module.addresses.list.execute(
                CustomerDetailsQuery(actor.business_id, actor, owner.id)
            )
        )
        == 1
    )


async def test_address_rejects_invalid_input_and_cross_customer_ids() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    owner = await module.customers.create.execute(CreateCustomerCommand(actor.business_id, actor))
    other = await module.customers.create.execute(CreateCustomerCommand(actor.business_id, actor))
    with pytest.raises(CustomerValidationError):
        await module.addresses.add.execute(
            AddAddressCommand(actor.business_id, actor, owner.id, "", "OM", "Road", "Muscat")
        )
    address = await module.addresses.add.execute(
        AddAddressCommand(actor.business_id, actor, owner.id, "Home", "OM", "Road", "Muscat")
    )
    with pytest.raises(CustomerNotFoundError):
        await module.addresses.set_default.execute(
            CustomerChildMutation(actor.business_id, actor, other.id, address.id)
        )
