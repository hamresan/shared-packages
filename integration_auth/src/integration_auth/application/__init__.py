"""Public application API for integration-auth."""

from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.application.errors import (
    IntegrationAuthenticationError,
    IntegrationClientNotFoundError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
    ReplayDetectedError,
    ReplayProtectionError,
    TimestampOutsideToleranceError,
)
from integration_auth.application.services import (
    AuthenticateIntegrationRequestService,
    ReplayProtector,
)

__all__ = (
    "AuthenticateIntegrationRequest",
    "AuthenticateIntegrationRequestService",
    "IntegrationAuthenticationError",
    "IntegrationClientNotFoundError",
    "InvalidIntegrationSignatureError",
    "NoUsableCredentialError",
    "ReplayDetectedError",
    "ReplayProtectionError",
    "ReplayProtector",
    "TimestampOutsideToleranceError",
)
