from customer.application.contracts import Clock, CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.models.profile_detail_commands import CustomerDetailsQuery
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.domain.errors import CustomerNotFoundError


class UnlinkInternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        clock: Clock,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.clock = clock

    async def execute(self, query: CustomerDetailsQuery) -> None:
        self.scope.require_matching_business(query.business_id, query.actor)
        await self.authorizer.require_permission(
            query.actor, CustomerPermission.IDENTITY_LINK, query.customer_id
        )
        async with self.uow(query.business_id) as transaction:
            link = await transaction.internal_identities.find_by_customer(
                query.business_id, query.customer_id
            )
            if link is None:
                raise CustomerNotFoundError("Internal identity association not found")
            link.revoked_at = self.clock.now()
            await transaction.internal_identities.revoke(link)
            await transaction.commit()
