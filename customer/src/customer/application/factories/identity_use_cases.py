"""Identity capability composition, isolated from facade and domain logic."""

from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
    IdentityVerifier,
)
from customer.application.contracts.external_identity_evidence import (
    ExternalIdentityEvidenceVerifier,
)
from customer.application.external_identity_use_cases import ExternalIdentityUseCases
from customer.application.factories.customer import CustomerFactory
from customer.application.factories.external_identity import ExternalIdentityFactory
from customer.application.internal_identity_use_cases import InternalIdentityUseCases
from customer.application.mapping.identity_resolution import IdentityResolutionMapper
from customer.application.policies.customer_scope import CustomerScopePolicy
from customer.application.services.find_external_identity import FindExternalIdentityService
from customer.application.services.get_or_create_external_identity import (
    GetOrCreateExternalIdentityService,
)
from customer.application.services.link_external_identity import LinkExternalIdentityService
from customer.application.services.link_internal_identity import LinkInternalIdentityService
from customer.application.services.record_external_verification import (
    RecordExternalVerificationService,
)
from customer.application.services.relink_external_identity import RelinkExternalIdentityService
from customer.application.services.resolve_internal_identity import ResolveInternalIdentityService
from customer.application.services.revoke_external_identity import RevokeExternalIdentityService
from customer.application.services.unlink_internal_identity import UnlinkInternalIdentityService
from customer.application.validation.customer_name import CustomerNameValidator
from customer.application.validation.external_identity import (
    ExternalIdentityEvidencePolicy,
    ExternalIdentityKeyValidator,
)


class IdentityUseCasesFactory:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        internal_verifier: IdentityVerifier,
        external_verifier: ExternalIdentityEvidenceVerifier,
        ids: IdentifierGenerator,
        clock: Clock,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.internal_verifier = internal_verifier
        self.external_verifier = external_verifier
        self.ids = ids
        self.clock = clock

    def build_internal(self) -> InternalIdentityUseCases:
        scope = CustomerScopePolicy()
        mapper = IdentityResolutionMapper()
        return InternalIdentityUseCases(
            link=LinkInternalIdentityService(
                self.uow,
                self.authorizer,
                scope,
                self.internal_verifier,
                self.ids,
                self.clock,
                mapper,
            ),
            unlink=UnlinkInternalIdentityService(
                self.uow,
                self.authorizer,
                scope,
                self.clock,
            ),
            resolve=ResolveInternalIdentityService(self.uow, self.authorizer, scope, mapper),
        )

    def build_external(self) -> ExternalIdentityUseCases:
        scope = CustomerScopePolicy()
        validator = ExternalIdentityKeyValidator()
        evidence_policy = ExternalIdentityEvidencePolicy()
        mapper = IdentityResolutionMapper()
        identity_factory = ExternalIdentityFactory()
        linker = LinkExternalIdentityService(
            self.uow,
            self.authorizer,
            scope,
            validator,
            self.external_verifier,
            evidence_policy,
            identity_factory,
            self.ids,
            self.clock,
            mapper,
        )
        return ExternalIdentityUseCases(
            find=FindExternalIdentityService(
                self.uow,
                self.authorizer,
                scope,
                validator,
                mapper,
            ),
            get_or_create=GetOrCreateExternalIdentityService(
                self.uow,
                self.authorizer,
                scope,
                validator,
                CustomerNameValidator(),
                self.external_verifier,
                evidence_policy,
                CustomerFactory(),
                identity_factory,
                self.ids,
                self.clock,
                mapper,
            ),
            link=linker,
            revoke=RevokeExternalIdentityService(
                self.uow,
                self.authorizer,
                scope,
                validator,
                self.clock,
            ),
            relink=RelinkExternalIdentityService(
                self.uow,
                self.authorizer,
                scope,
                validator,
                linker,
            ),
            record_verification=RecordExternalVerificationService(
                self.uow,
                self.authorizer,
                scope,
                validator,
                self.external_verifier,
                evidence_policy,
                mapper,
            ),
        )
