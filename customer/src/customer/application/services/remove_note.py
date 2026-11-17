from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.models.profile_detail_commands import CustomerChildMutation
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.domain.errors import CustomerNotFoundError


class RemoveNoteService:
    def __init__(self, uow: CustomerUnitOfWorkFactory, access: CustomerDetailAccessPolicy) -> None:
        self.uow = uow
        self.access = access

    async def execute(self, command: CustomerChildMutation) -> None:
        async with self.uow() as transaction:
            await self.access.require(
                transaction.customers,
                command.business_id,
                command.customer_id,
                command.actor,
                CustomerPermission.NOTES_WRITE,
                mutating=True,
            )
            removed = await transaction.notes.remove(
                command.business_id, command.customer_id, command.child_id
            )
            if not removed:
                raise CustomerNotFoundError("Note was not found")
            await transaction.commit()
