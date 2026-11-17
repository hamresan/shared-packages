"""Reusable authorization and ownership check for customer-owned details."""

from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.contracts import CustomerAuthorizer, CustomerRepository
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.domain.errors import CustomerNotFoundError


class CustomerDetailAccessPolicy:
    def __init__(self, scope: CustomerScopePolicy, authorizer: CustomerAuthorizer) -> None:
        self.scope = scope
        self.authorizer = authorizer

    async def require(
        self,
        repository: CustomerRepository,
        business_id: UUID,
        customer_id: UUID,
        actor: CustomerActor,
        permission: CustomerPermission,
        *,
        mutating: bool,
    ) -> None:
        self.scope.require_matching_business(business_id, actor)
        await self.authorizer.require_permission(actor, permission, customer_id)
        customer = await repository.get(business_id, customer_id)
        if customer is None:
            raise CustomerNotFoundError("Customer was not found")
        if mutating:
            customer.require_active()
