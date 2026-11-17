from customer.application.contracts import Clock, CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.models import CustomerResult, UpdateCustomerCommand
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.application.validation import CustomerNameValidator
from customer.domain.errors import CustomerNotFoundError, CustomerVersionConflictError


class UpdateCustomerService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: CustomerNameValidator,
        clock: Clock,
        mapper: CustomerResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: UpdateCustomerCommand) -> CustomerResult:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.UPDATE, command.customer_id
        )
        name = self.validator.normalize(command.display_name)
        async with self.uow() as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer was not found")
            if customer.version != command.expected_version:
                raise CustomerVersionConflictError("Customer version has changed")
            customer.update_profile(name, self.clock.now())
            await transaction.customers.save(customer, command.expected_version)
            await transaction.commit()
            return self.mapper.to_result(customer)
