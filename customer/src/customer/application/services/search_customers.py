from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.models import CustomerSearchQuery, CustomerSearchResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.application.validation import CustomerSearchValidator


class SearchCustomersService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: CustomerSearchValidator,
        mapper: CustomerResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.mapper = mapper

    async def execute(self, query: CustomerSearchQuery) -> CustomerSearchResult:
        self.scope.require_matching_business(query.business_id, query.actor)
        await self.authorizer.require_permission(query.actor, CustomerPermission.READ)
        self.validator.validate(query)
        async with self.uow() as transaction:
            customers = await transaction.customers.search(
                query.business_id, query.name_contains, query.offset, query.limit + 1
            )
            return CustomerSearchResult(
                items=tuple(self.mapper.to_result(c) for c in customers[: query.limit]),
                has_more=len(customers) > query.limit,
            )
