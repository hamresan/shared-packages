from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
)
from customer.application.contracts.external_identity_evidence import (
    ExternalIdentityEvidenceVerifier,
)
from customer.application.factories.external_identity import ExternalIdentityFactory
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.models.external_identity_commands import LinkExternalIdentityCommand
from customer.application.models.identity_resolution import CustomerResolution
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.validation.external_identity import (
    ExternalIdentityEvidencePolicy,
    ExternalIdentityKeyValidator,
)
from customer.domain.errors import CustomerIdentityConflictError, CustomerNotFoundError


class LinkExternalIdentityService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: ExternalIdentityKeyValidator,
        verifier: ExternalIdentityEvidenceVerifier,
        evidence_policy: ExternalIdentityEvidencePolicy,
        factory: ExternalIdentityFactory,
        identifiers: IdentifierGenerator,
        clock: Clock,
        mapper: IdentityResolutionMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.verifier = verifier
        self.evidence_policy = evidence_policy
        self.factory = factory
        self.identifiers = identifiers
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: LinkExternalIdentityCommand) -> CustomerResolution:
        self.scope.require_matching_business(command.key.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.EXTERNAL_IDENTITY_MANAGE, command.customer_id
        )
        key = self.validator.normalize(command.key)
        evidence = await self.verifier.require_verified(key, command.evidence_reference)
        self.evidence_policy.require_matching(key, evidence)
        async with self.uow(command.key.business_id) as transaction:
            customer = await transaction.customers.get(key.business_id, command.customer_id)
            if customer is None:
                raise CustomerNotFoundError("Customer not found")
            customer.require_active()
            active = await transaction.external_identities.find_active(key)
            if active is not None:
                if active.customer_id != customer.id:
                    raise CustomerIdentityConflictError("External identity already linked")
                active.record_verification(evidence.method, evidence.verified_at)
                await transaction.external_identities.save(active)
                await transaction.commit()
                return self.mapper.to_external(active)
            previous = await transaction.external_identities.find_latest(key)
            self.evidence_policy.require_after_revocation(previous, evidence)
            link = self.factory.create(
                self.identifiers.new_id(),
                customer.id,
                key,
                evidence.method,
                evidence.verified_at,
                self.clock.now(),
            )
            await transaction.external_identities.add(link)
            await transaction.commit()
            return self.mapper.to_external(link)
