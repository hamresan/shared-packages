"""Deterministic provisioning identifier generators for tests."""

from integration_auth.application.contracts.provisioning.id_generators import (
    IntegrationClientIdGenerator,
    IntegrationCredentialIdGenerator,
)
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


class FixedIntegrationClientIdGenerator(IntegrationClientIdGenerator):
    """Return one configured client identifier."""

    def __init__(self, value: str = "client-new") -> None:
        self._client_id = IntegrationClientId(value)

    def generate(self) -> IntegrationClientId:
        return self._client_id


class FixedIntegrationCredentialIdGenerator(IntegrationCredentialIdGenerator):
    """Return one configured credential identifier."""

    def __init__(self, value: str = "credential-new") -> None:
        self._credential_id = IntegrationCredentialId(value)

    def generate(self) -> IntegrationCredentialId:
        return self._credential_id
