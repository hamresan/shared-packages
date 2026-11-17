"""Host-injected example: optimistic customer update."""

from uuid import UUID

from customer import (
    CustomerActor,
    CustomerModule,
    CustomerVersionConflictError,
    UpdateCustomerCommand,
)


async def rename_if_unchanged(
    module: CustomerModule, actor: CustomerActor, customer_id: UUID, expected_version: int
) -> bool:
    try:
        await module.customers.update.execute(
            UpdateCustomerCommand(
                actor.business_id, actor, customer_id, expected_version, "Alex R."
            )
        )
    except CustomerVersionConflictError:
        # The caller should re-read and review the conflicting edit.
        return False
    return True
