from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping.contact_result import ContactResultMapper
from customer.application.models.contact_commands import UpdateContactCommand
from customer.application.models.contact_result import ContactResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.application.validation.contact_value import ContactValueNormalizer
from customer.domain.errors import CustomerNotFoundError


class UpdateContactService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        normalizer: ContactValueNormalizer,
        mapper: ContactResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.normalizer = normalizer
        self.mapper = mapper

    async def execute(self, command: UpdateContactCommand) -> ContactResult:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.UPDATE, command.customer_id
        )
        async with self.uow() as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            contact = await transaction.contacts.get(
                command.business_id, command.customer_id, command.contact_id
            )
            if customer is None or contact is None:
                raise CustomerNotFoundError("Contact was not found")
            customer.require_active()
            contact.value = self.normalizer.normalize(contact.kind, command.value)
            contact.verified_at = None
            contact.verification_method = None
            await transaction.contacts.save(contact)
            await transaction.commit()
            return self.mapper.to_result(contact)
