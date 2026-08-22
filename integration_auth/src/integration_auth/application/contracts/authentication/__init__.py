"""Authentication application contracts."""

from .clock import Clock
from .credential_secret_provider import CredentialSecretProvider
from .integration_client_repository import IntegrationClientRepository
from .integration_credential_repository import IntegrationCredentialRepository
from .request_authenticator import IntegrationRequestAuthenticator

__all__ = (
    "Clock",
    "CredentialSecretProvider",
    "IntegrationClientRepository",
    "IntegrationCredentialRepository",
    "IntegrationRequestAuthenticator",
)
