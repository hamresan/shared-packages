from customer.application.contracts import Clock, CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.models.external_identity_commands import RevokeExternalIdentityCommand
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.validation.external_identity import ExternalIdentityKeyValidator
from customer.domain.errors import CustomerNotFoundError


class RevokeExternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: ExternalIdentityKeyValidator,
        clock: Clock,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.clock = clock

    async def execute(self, command: RevokeExternalIdentityCommand) -> None:
        self.scope.require_matching_business(command.key.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.EXTERNAL_IDENTITY_MANAGE, command.customer_id
        )
        key = self.validator.normalize(command.key)
        async with self.uow() as transaction:
            identity = await transaction.external_identities.get_active_for_customer(
                key, command.customer_id
            )
            if identity is None:
                raise CustomerNotFoundError("External identity was not found")
            identity.revoke(self.clock.now())
            await transaction.external_identities.save(identity)
            await transaction.commit()
