"""Authentication application contracts."""

from integration_auth.application.contracts.authentication.clock import Clock
from integration_auth.application.contracts.authentication.credential_secret_provider import (
    CredentialSecretProvider,
)
from integration_auth.application.contracts.authentication.integration_client_repository import (
    IntegrationClientRepository,
)
from integration_auth.application.contracts.authentication.integration_credential_repository import (
    IntegrationCredentialRepository,
)

__all__ = (
    "Clock",
    "CredentialSecretProvider",
    "IntegrationClientRepository",
    "IntegrationCredentialRepository",
)
