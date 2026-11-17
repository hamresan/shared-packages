from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
    IdentityVerifier,
)
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.models.identity_resolution import InternalIdentityResolution
from customer.application.models.internal_identity_commands import LinkInternalIdentityCommand
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.domain.errors import CustomerIdentityConflictError, CustomerNotFoundError
from customer.domain.identity_link import CustomerIdentityLink


class LinkInternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        verifier: IdentityVerifier,
        ids: IdentifierGenerator,
        clock: Clock,
        mapper: IdentityResolutionMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.verifier = verifier
        self.ids = ids
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: LinkInternalIdentityCommand) -> InternalIdentityResolution:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.IDENTITY_LINK, command.customer_id
        )
        await self.verifier.require_linkable_user(
            command.identity_user_id, command.actor, command.customer_id
        )
        async with self.uow(command.business_id) as transaction:
            customer = await transaction.customers.get(command.business_id, command.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer not found")
            customer.require_active()
            by_customer = await transaction.internal_identities.find_by_customer(
                command.business_id, command.customer_id
            )
            by_user = await transaction.internal_identities.find_by_user(
                command.business_id, command.identity_user_id
            )
            if by_customer is not None or by_user is not None:
                if (
                    by_customer is not None
                    and by_customer.identity_user_id == command.identity_user_id
                    and by_user is not None
                    and by_user.customer_id == command.customer_id
                ):
                    return self.mapper.to_internal(by_customer)
                raise CustomerIdentityConflictError("Active identity association conflicts")
            link = CustomerIdentityLink(
                self.ids.new_id(),
                command.business_id,
                command.customer_id,
                command.identity_user_id,
                self.clock.now(),
            )
            await transaction.internal_identities.add(link)
            await transaction.commit()
            return self.mapper.to_internal(link)
