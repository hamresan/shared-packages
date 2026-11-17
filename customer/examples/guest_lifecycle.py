"""Host-injected example: idempotent guest creation and authorized profile read."""

from customer import (
    CreateCustomerCommand,
    CustomerActor,
    CustomerModule,
    CustomerResult,
    GetCustomerQuery,
)


async def create_guest_and_read(
    module: CustomerModule, actor: CustomerActor, operation_key: str
) -> tuple[CustomerResult, CustomerResult]:
    """Use a stable host operation key across retries, without registering an account."""
    created = await module.customers.create.execute(
        CreateCustomerCommand(
            business_id=actor.business_id,
            actor=actor,
            display_name="Alex Rivera",
            idempotency_key=operation_key,
        )
    )
    profile = await module.customers.get.execute(
        GetCustomerQuery(
            business_id=actor.business_id,
            actor=actor,
            customer_id=created.id,
        )
    )
    return created, profile
