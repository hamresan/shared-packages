from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.models.identity_resolution import InternalIdentityResolution
from customer.application.models.internal_identity_commands import ResolveInternalIdentityQuery
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy


class ResolveInternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        mapper: IdentityResolutionMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.mapper = mapper

    async def execute(
        self, query: ResolveInternalIdentityQuery
    ) -> InternalIdentityResolution | None:
        self.scope.require_matching_business(query.business_id, query.actor)
        await self.authorizer.require_permission(query.actor, CustomerPermission.IDENTITY_RESOLVE)
        async with self.uow(query.business_id) as transaction:
            link = await transaction.internal_identities.find_by_user(
                query.business_id, query.identity_user_id
            )
            return self.mapper.to_internal(link) if link is not None else None
