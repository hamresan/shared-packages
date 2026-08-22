"""Provisioning identifier generator contracts."""

from typing import Protocol

from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


class IntegrationClientIdGenerator(Protocol):
    """Generate integration client identifiers."""

    def generate(self) -> IntegrationClientId: ...


class IntegrationCredentialIdGenerator(Protocol):
    """Generate integration credential identifiers."""

    def generate(self) -> IntegrationCredentialId: ...
