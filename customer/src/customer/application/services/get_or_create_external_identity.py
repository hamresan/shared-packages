from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
)
from customer.application.contracts.external_identity_evidence import (
    ExternalIdentityEvidenceVerifier,
)
from customer.application.factories.customer import CustomerFactory
from customer.application.factories.external_identity import ExternalIdentityFactory
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.models.external_identity_commands import (
    GetOrCreateExternalIdentityCommand,
)
from customer.application.models.identity_resolution import CustomerResolution
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.validation.customer_name import CustomerNameValidator
from customer.application.validation.external_identity import (
    ExternalIdentityEvidencePolicy,
    ExternalIdentityKeyValidator,
)
from customer.domain.customer import CustomerStatus
from customer.domain.errors import (
    CustomerExternalIdentityRaceError,
    CustomerIdentityConflictError,
    CustomerNotFoundError,
)
from customer.domain.external_identity import ExternalIdentityStatus


class GetOrCreateExternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        key_validator: ExternalIdentityKeyValidator,
        name_validator: CustomerNameValidator,
        verifier: ExternalIdentityEvidenceVerifier,
        evidence_policy: ExternalIdentityEvidencePolicy,
        customer_factory: CustomerFactory,
        identity_factory: ExternalIdentityFactory,
        identifiers: IdentifierGenerator,
        clock: Clock,
        mapper: IdentityResolutionMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.key_validator = key_validator
        self.name_validator = name_validator
        self.verifier = verifier
        self.evidence_policy = evidence_policy
        self.customer_factory = customer_factory
        self.identity_factory = identity_factory
        self.identifiers = identifiers
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: GetOrCreateExternalIdentityCommand) -> CustomerResolution:
        self.scope.require_matching_business(command.key.business_id, command.actor)
        await self.authorizer.require_permission(command.actor, CustomerPermission.CREATE)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.EXTERNAL_IDENTITY_MANAGE
        )
        key = self.key_validator.normalize(command.key)
        name = self.name_validator.normalize(command.display_name)
        evidence = await self.verifier.require_verified(key, command.evidence_reference)
        self.evidence_policy.require_matching(key, evidence)
        try:
            async with self.uow(key.business_id) as transaction:
                active = await transaction.external_identities.find_active(key)
                if active is not None:
                    customer = await transaction.customers.get(key.business_id, active.customer_id)
                    if customer is None or customer.status is CustomerStatus.ERASED:
                        raise CustomerNotFoundError("Linked customer is unavailable")
                    return self.mapper.to_external(active)
                previous = await transaction.external_identities.find_latest(key)
                if previous is not None and previous.status is ExternalIdentityStatus.REVOKED:
                    raise CustomerIdentityConflictError("Revoked identity requires explicit relink")
                customer = self.customer_factory.create(
                    self.identifiers.new_id(), key.business_id, name, self.clock.now()
                )
                identity = self.identity_factory.create(
                    self.identifiers.new_id(),
                    customer.id,
                    key,
                    evidence.method,
                    evidence.verified_at,
                    self.clock.now(),
                )
                await transaction.customers.add(customer)
                await transaction.external_identities.add(identity)
                await transaction.commit_audited(
                    command.actor, "external_identity.get_or_create", customer.id
                )
                return self.mapper.to_external(identity)
        except CustomerExternalIdentityRaceError:
            # The losing transaction has exited and rolled back. Read committed
            # state in a new tenant-scoped transaction; never retry the insert.
            async with self.uow(key.business_id) as transaction:
                active = await transaction.external_identities.find_active(key)
                if active is None:
                    raise CustomerIdentityConflictError(
                        "Concurrent external identity cannot be resolved"
                    ) from None
                customer = await transaction.customers.get(key.business_id, active.customer_id)
                if customer is None or customer.status is CustomerStatus.ERASED:
                    raise CustomerNotFoundError("Linked customer is unavailable") from None
                return self.mapper.to_external(active)
