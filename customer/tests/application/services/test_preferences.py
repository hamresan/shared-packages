from uuid import uuid4

import pytest

from customer.application.models import CreateCustomerCommand
from customer.application.models.preference_commands import (
    RemovePreferenceCommand,
    SetPreferenceCommand,
)
from customer.application.models.profile_detail_commands import CustomerDetailsQuery
from customer.domain.errors import CustomerNotFoundError, CustomerValidationError
from tests.support.factories.customer_module import build_actor, build_customer_module


async def test_preference_upsert_is_unique_within_customer() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    initial = await module.preferences.set.execute(
        SetPreferenceCommand(actor.business_id, actor, customer.id, " Locale ", "en")
    )
    updated = await module.preferences.set.execute(
        SetPreferenceCommand(actor.business_id, actor, customer.id, "locale", "fr")
    )
    assert initial.id == updated.id
    assert updated.value == "fr"
    assert (
        len(
            await module.preferences.list.execute(
                CustomerDetailsQuery(actor.business_id, actor, customer.id)
            )
        )
        == 1
    )
    await module.preferences.remove.execute(
        RemovePreferenceCommand(actor.business_id, actor, customer.id, "LOCALE")
    )
    assert not await module.preferences.list.execute(
        CustomerDetailsQuery(actor.business_id, actor, customer.id)
    )
    with pytest.raises(CustomerNotFoundError):
        await module.preferences.remove.execute(
            RemovePreferenceCommand(actor.business_id, actor, customer.id, "locale")
        )


@pytest.mark.parametrize("key,value", [("invalid key", "x"), ("ok", "x" * 501), ("ok", [1])])
async def test_preference_validation_rejects_unsupported_values(key: str, value: object) -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    with pytest.raises(CustomerValidationError):
        await module.preferences.set.execute(
            SetPreferenceCommand(actor.business_id, actor, customer.id, key, value)  # type: ignore[arg-type]
        )
