"""Framework-independent Customer composition entry point."""

from dataclasses import dataclass

from customer.application.contracts import (
    CustomerAuthorizer,
    CustomerUnitOfWorkFactory,
    IdentityVerifier,
)


@dataclass(frozen=True, slots=True)
class CustomerModuleConfig:
    """Host-supplied dependencies; no engine or provider is created here."""

    unit_of_work_factory: CustomerUnitOfWorkFactory
    authorizer: CustomerAuthorizer
    identity_verifier: IdentityVerifier


class CustomerModule:
    """Stable public facade to which feature use cases are added by stage."""

    def __init__(self, config: CustomerModuleConfig) -> None:
        self._config = config

    @property
    def config(self) -> CustomerModuleConfig:
        """Expose immutable host configuration until capability groups are implemented."""
        return self._config
