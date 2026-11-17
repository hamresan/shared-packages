from customer.application.contracts import CustomerAuthorizer, CustomerUnitOfWorkFactory
from customer.application.contracts.external_identity_evidence import (
    ExternalIdentityEvidenceVerifier,
)
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.models.external_identity_commands import (
    RecordExternalIdentityVerificationCommand,
)
from customer.application.models.identity_resolution import CustomerResolution
from customer.application.permissions import CustomerPermission
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.validation.external_identity import (
    ExternalIdentityEvidencePolicy,
    ExternalIdentityKeyValidator,
)
from customer.domain.errors import CustomerNotFoundError


class RecordExternalVerificationService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: ExternalIdentityKeyValidator,
        verifier: ExternalIdentityEvidenceVerifier,
        policy: ExternalIdentityEvidencePolicy,
        mapper: IdentityResolutionMapper,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.verifier = verifier
        self.policy = policy
        self.mapper = mapper

    async def execute(
        self, command: RecordExternalIdentityVerificationCommand
    ) -> CustomerResolution:
        self.scope.require_matching_business(command.key.business_id, command.actor)
        await self.authorizer.require_permission(
            command.actor, CustomerPermission.EXTERNAL_IDENTITY_MANAGE, command.customer_id
        )
        key = self.validator.normalize(command.key)
        evidence = await self.verifier.require_verified(key, command.evidence_reference)
        self.policy.require_matching(key, evidence)
        async with self.uow() as transaction:
            active = await transaction.external_identities.get_active_for_customer(
                key, command.customer_id
            )
            if active is None:
                raise CustomerNotFoundError("External identity was not found")
            active.record_verification(evidence.method, evidence.verified_at)
            await transaction.external_identities.save(active)
            await transaction.commit()
            return self.mapper.to_external(active)
