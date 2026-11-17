from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
)
from customer.application.mapping.contact_result import ContactResultMapper
from customer.application.models.contact_commands import AddContactCommand
from customer.application.models.contact_result import ContactResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.application.validation.contact_value import ContactValueNormalizer
from customer.domain.contact import CustomerContact
from customer.domain.errors import CustomerNotFoundError


class AddContactService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        normalizer: ContactValueNormalizer,
        identifiers: IdentifierGenerator,
        clock: Clock,
        mapper: ContactResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.normalizer = normalizer
        self.identifiers = identifiers
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: AddContactCommand) -> ContactResult:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.UPDATE, command.customer_id
        )
        normalized = self.normalizer.normalize(command.kind, command.value)
        async with self.uow() as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer was not found")
            customer.require_active()
            if command.is_primary:
                await transaction.contacts.unset_primary(
                    command.business_id, command.customer_id, command.kind
                )
            contact = CustomerContact(
                id=self.identifiers.new_id(),
                business_id=command.business_id,
                customer_id=command.customer_id,
                kind=command.kind,
                value=normalized,
                is_primary=command.is_primary,
                created_at=self.clock.now(),
            )
            await transaction.contacts.add(contact)
            await transaction.commit()
            return self.mapper.to_result(contact)
