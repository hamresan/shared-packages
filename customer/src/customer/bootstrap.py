"""Framework-independent Customer composition entry point."""

from dataclasses import dataclass

from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerCreationFingerprinter,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
    IdentityVerifier,
)
from customer.application.customer_use_cases import CustomerUseCases
from customer.application.factories import CustomerFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.policies import CustomerScopePolicy
from customer.application.services import (
    ArchiveCustomerService,
    CreateCustomerService,
    GetCustomerService,
    ReactivateCustomerService,
    SearchCustomersService,
    UpdateCustomerService,
)
from customer.application.validation import CustomerNameValidator, CustomerSearchValidator


@dataclass(frozen=True, slots=True)
class CustomerModuleConfig:
    """Host-supplied dependencies; no engine or provider is created here."""

    unit_of_work_factory: CustomerUnitOfWorkFactory
    authorizer: CustomerAuthorizer
    identity_verifier: IdentityVerifier
    clock: Clock
    identifiers: IdentifierGenerator
    creation_fingerprinter: CustomerCreationFingerprinter


class CustomerModule:
    """Stable public facade to which feature use cases are added by stage."""

    def __init__(self, config: CustomerModuleConfig) -> None:
        self._config = config
        scope = CustomerScopePolicy()
        mapper = CustomerResultMapper()
        names = CustomerNameValidator()
        self._customers = CustomerUseCases(
            create=CreateCustomerService(
                config.unit_of_work_factory,
                config.authorizer,
                scope,
                names,
                CustomerFactory(),
                config.identifiers,
                config.clock,
                mapper,
                config.creation_fingerprinter,
            ),
            get=GetCustomerService(config.unit_of_work_factory, config.authorizer, scope, mapper),
            update=UpdateCustomerService(
                config.unit_of_work_factory, config.authorizer, scope, names, config.clock, mapper
            ),
            archive=ArchiveCustomerService(
                config.unit_of_work_factory, config.authorizer, scope, config.clock, mapper
            ),
            reactivate=ReactivateCustomerService(
                config.unit_of_work_factory, config.authorizer, scope, config.clock, mapper
            ),
            search=SearchCustomersService(
                config.unit_of_work_factory,
                config.authorizer,
                scope,
                CustomerSearchValidator(),
                mapper,
            ),
        )

    @property
    def customers(self) -> CustomerUseCases:
        return self._customers

    @property
    def config(self) -> CustomerModuleConfig:
        """Expose immutable host configuration until capability groups are implemented."""
        return self._config
