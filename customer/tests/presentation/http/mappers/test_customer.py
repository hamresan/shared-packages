from uuid import uuid4

from customer.application.models import CreateCustomerCommand, UpdateCustomerCommand
from customer.presentation.http.dto import CustomerCreateBody, CustomerUpdateBody
from customer.presentation.http.mappers import CustomerHttpMapper
from tests.support.factories.customer_module import build_actor, build_customer_module


async def test_customer_http_mapper_builds_commands_and_minimal_response() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    mapper = CustomerHttpMapper()
    created_command = mapper.to_create_command(
        actor.business_id, actor, CustomerCreateBody(display_name="Alex"), "stable-key"
    )
    assert isinstance(created_command, CreateCustomerCommand)
    assert created_command.actor == actor and created_command.idempotency_key == "stable-key"
    created = await module.customers.create.execute(created_command)
    query = mapper.to_get_query(actor.business_id, actor, created.id)
    assert query.customer_id == created.id

    update = mapper.to_update_command(
        actor.business_id,
        actor,
        created.id,
        CustomerUpdateBody(display_name="Alex R.", expected_version=created.version),
    )
    assert isinstance(update, UpdateCustomerCommand)
    assert update.expected_version == created.version

    response = mapper.to_response(created)
    assert response.id == created.id
    assert "notes" not in response.model_dump()
    assert "contacts" not in response.model_dump()
