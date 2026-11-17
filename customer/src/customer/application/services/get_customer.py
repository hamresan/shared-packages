from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.models import CustomerResult, GetCustomerQuery
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.domain.errors import CustomerNotFoundError


class GetCustomerService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        mapper: CustomerResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.mapper = mapper

    async def execute(self, query: GetCustomerQuery) -> CustomerResult:
        self.scope.require_matching_business(query.business_id, query.actor)
        await self.authorizer.require_permission(
            query.actor, CustomerPermission.READ, query.customer_id
        )
        async with self.uow() as transaction:
            customer = await transaction.customers.get(query.business_id, query.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer was not found")
            return self.mapper.to_result(customer)
