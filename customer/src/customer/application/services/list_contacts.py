from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping.contact_result import ContactResultMapper
from customer.application.models.contact_commands import ListContactsQuery
from customer.application.models.contact_result import ContactResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.domain.errors import CustomerNotFoundError


class ListContactsService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        mapper: ContactResultMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.mapper = mapper

    async def execute(self, query: ListContactsQuery) -> tuple[ContactResult, ...]:
        self.scope.require_matching_business(query.business_id, query.actor)
        await self.authorizer.require_permission(
            query.actor, CustomerPermission.READ, query.customer_id
        )
        async with self.uow(query.business_id) as transaction:
            customer = await transaction.customers.get(query.business_id, query.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer was not found")
            contacts = await transaction.contacts.list_for_customer(
                query.business_id, query.customer_id
            )
            return tuple(self.mapper.to_result(contact) for contact in contacts)
