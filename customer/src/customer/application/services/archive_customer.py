from customer.application.contracts import Clock, CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.models import CustomerMutationCommand, CustomerResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.domain.errors import CustomerNotFoundError, CustomerVersionConflictError


class ArchiveCustomerService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        clock: Clock,
        mapper: CustomerResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: CustomerMutationCommand) -> CustomerResult:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.ARCHIVE, command.customer_id
        )
        async with self.uow(command.business_id) as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer was not found")
            if customer.version != command.expected_version:
                raise CustomerVersionConflictError("Customer version has changed")
            customer.archive(self.clock.now())
            await transaction.customers.save(customer, command.expected_version)
            await transaction.commit()
            return self.mapper.to_result(customer)
