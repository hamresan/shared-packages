"""Application error public API."""

from integration_auth.application.errors.authentication import (
    IntegrationAuthenticationError,
    IntegrationClientNotFoundError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
)
from integration_auth.application.errors.authorization import IntegrationAuthorizationError
from integration_auth.application.errors.provisioning import (
    IntegrationProvisioningError,
    ProvisioningClientNotFoundError,
    ProvisioningCredentialNotFoundError,
)
from integration_auth.application.errors.replay import (
    ReplayDetectedError,
    ReplayProtectionError,
    TimestampOutsideToleranceError,
)

__all__ = (
    "IntegrationAuthenticationError",
    "IntegrationAuthorizationError",
    "IntegrationClientNotFoundError",
    "IntegrationProvisioningError",
    "InvalidIntegrationSignatureError",
    "NoUsableCredentialError",
    "ProvisioningClientNotFoundError",
    "ProvisioningCredentialNotFoundError",
    "ReplayDetectedError",
    "ReplayProtectionError",
    "TimestampOutsideToleranceError",
)
