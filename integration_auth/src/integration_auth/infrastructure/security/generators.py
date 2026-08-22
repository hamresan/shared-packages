"""Secure provisioning generators backed by Python's standard library."""

import secrets
import uuid

from integration_auth.application.contracts.provisioning.id_generators import (
    IntegrationClientIdGenerator,
    IntegrationCredentialIdGenerator,
)
from integration_auth.application.contracts.provisioning.secrets import CredentialSecretGenerator
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


class UuidIntegrationClientIdGenerator(IntegrationClientIdGenerator):
    """Generate opaque client IDs using UUID4 entropy."""

    def generate(self) -> IntegrationClientId:
        return IntegrationClientId(str(uuid.uuid4()))


class UuidIntegrationCredentialIdGenerator(IntegrationCredentialIdGenerator):
    """Generate opaque credential IDs using UUID4 entropy."""

    def generate(self) -> IntegrationCredentialId:
        return IntegrationCredentialId(str(uuid.uuid4()))


class SecretsCredentialSecretGenerator(CredentialSecretGenerator):
    """Generate 256-bit credential secrets."""

    def generate(self) -> bytes:
        return secrets.token_bytes(32)
