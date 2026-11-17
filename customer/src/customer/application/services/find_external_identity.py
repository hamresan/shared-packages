from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.models.external_identity_commands import FindExternalIdentityQuery
from customer.application.models.identity_resolution import CustomerResolution
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.validation.external_identity import ExternalIdentityKeyValidator
from customer.domain.customer import CustomerStatus


class FindExternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: ExternalIdentityKeyValidator,
        mapper: IdentityResolutionMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.mapper = mapper

    async def execute(self, query: FindExternalIdentityQuery) -> CustomerResolution | None:
        self.scope.require_matching_business(query.key.business_id, query.actor)
        await self.authorizer.require_permission(
            query.actor, CustomerPermission.EXTERNAL_IDENTITY_LOOKUP
        )
        key = self.validator.normalize(query.key)
        async with self.uow() as transaction:
            identity = await transaction.external_identities.find_active(key)
            if identity is None:
                return None
            customer = await transaction.customers.get(key.business_id, identity.customer_id)
            if customer is None or customer.status is CustomerStatus.ERASED:
                return None
            return self.mapper.to_external(identity)
