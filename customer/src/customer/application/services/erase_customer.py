"""Terminal, authorized privacy erasure in one auditable transaction."""

from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerErasurePolicy,
    CustomerUnitOfWorkFactory,
)
from customer.application.mapping import CustomerResultMapper
from customer.application.models import CustomerMutationCommand, CustomerResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.domain.errors import (
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerVersionConflictError,
)


class EraseCustomerService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        policy: CustomerErasurePolicy | None,
        clock: Clock,
        mapper: CustomerResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.policy = policy
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: CustomerMutationCommand) -> CustomerResult:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.ERASE, command.customer_id
        )
        if self.policy is None:
            raise CustomerPermissionDeniedError("Host erasure policy is required")
        await self.policy.require_allowed(command.actor, command.business_id, command.customer_id)
        async with self.uow(command.business_id) as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer was not found")
            if customer.version != command.expected_version:
                raise CustomerVersionConflictError("Customer version has changed")
            customer.erase(self.clock.now())
            await transaction.erasure.erase_children(command.business_id, customer.id)
            await transaction.customers.save(customer, command.expected_version)
            await transaction.commit_audited(command.actor, "customer.erase", customer.id)
            return self.mapper.to_result(customer)
