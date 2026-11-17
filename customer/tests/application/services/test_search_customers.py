from uuid import uuid4

import pytest

from customer.application.models import CreateCustomerCommand, CustomerSearchQuery
from customer.domain import CustomerValidationError
from tests.support.factories.customer_module import build_actor, build_customer_module


async def test_search_scope_name_order_and_pagination() -> None:
    module, _ = build_customer_module()
    business = uuid4()
    actor = build_actor(business)
    other = build_actor(uuid4())
    for name in ("Alice", "Alina", "Bob"):
        await module.customers.create.execute(CreateCustomerCommand(business, actor, name))
    await module.customers.create.execute(CreateCustomerCommand(other.business_id, other, "Alana"))

    matches = await module.customers.search.execute(CustomerSearchQuery(business, actor, "ALI"))
    assert {entry.display_name for entry in matches.items} == {"Alice", "Alina"}
    assert not matches.has_more
    page = await module.customers.search.execute(CustomerSearchQuery(business, actor, limit=1))
    assert len(page.items) == 1
    assert page.has_more
    second = await module.customers.search.execute(
        CustomerSearchQuery(business, actor, offset=1, limit=1)
    )
    assert second.items[0].id != page.items[0].id


@pytest.mark.parametrize(
    "offset,limit,name", [(-1, 20, None), (0, 0, None), (0, 101, None), (0, 20, "x" * 201)]
)
async def test_invalid_search_parameters(offset: int, limit: int, name: str | None) -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    with pytest.raises(CustomerValidationError):
        await module.customers.search.execute(
            CustomerSearchQuery(actor.business_id, actor, name, offset, limit)
        )
