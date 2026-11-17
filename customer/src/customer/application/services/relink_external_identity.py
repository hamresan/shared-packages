from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.models.external_identity_commands import LinkExternalIdentityCommand
from customer.application.models.identity_resolution import CustomerResolution
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.services.link_external_identity import LinkExternalIdentityService
from customer.application.validation.external_identity import ExternalIdentityKeyValidator
from customer.domain.errors import CustomerIdentityConflictError, CustomerNotFoundError
from customer.domain.external_identity import ExternalIdentityStatus


class RelinkExternalIdentityService:
    """Explicit replacement path after revocation; re-verifies through link service."""

    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: ExternalIdentityKeyValidator,
        link_service: LinkExternalIdentityService,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.link_service = link_service

    async def execute(self, command: LinkExternalIdentityCommand) -> CustomerResolution:
        self.scope.require_matching_business(command.key.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.EXTERNAL_IDENTITY_MANAGE, command.customer_id
        )
        key = self.validator.normalize(command.key)
        async with self.uow() as transaction:
            previous = await transaction.external_identities.find_latest(key)
            if previous is None:
                raise CustomerNotFoundError("No previous external identity exists")
            if previous.status is not ExternalIdentityStatus.REVOKED:
                raise CustomerIdentityConflictError("External identity must be revoked first")
        return await self.link_service.execute(command)
