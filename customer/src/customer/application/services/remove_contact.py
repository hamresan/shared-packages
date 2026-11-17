from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.models.contact_commands import ContactMutationCommand
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.domain.errors import CustomerNotFoundError


class RemoveContactService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope

    async def execute(self, command: ContactMutationCommand) -> None:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.UPDATE, command.customer_id
        )
        async with self.uow(command.business_id) as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            contact = await transaction.contacts.get(
                command.business_id, command.customer_id, command.contact_id
            )
            if customer is None or contact is None:
                raise CustomerNotFoundError("Contact was not found")
            customer.require_active()
            await transaction.contacts.remove(
                command.business_id, command.customer_id, command.contact_id
            )
            await transaction.commit()
