"""Public application API for integration-auth."""

from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.application.dto.authorization import (
    AuthorizationDecisionReason,
    AuthorizationResult,
)
from integration_auth.application.errors import (
    IntegrationAuthenticationError,
    IntegrationAuthorizationError,
    IntegrationClientNotFoundError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
    ReplayDetectedError,
    ReplayProtectionError,
    TimestampOutsideToleranceError,
)
from integration_auth.application.services import (
    AuthenticateIntegrationRequestService,
    IntegrationAuthorizer,
    ReplayProtector,
)

__all__ = (
    "AuthenticateIntegrationRequest",
    "AuthenticateIntegrationRequestService",
    "AuthorizationDecisionReason",
    "AuthorizationResult",
    "IntegrationAuthenticationError",
    "IntegrationAuthorizationError",
    "IntegrationAuthorizer",
    "IntegrationClientNotFoundError",
    "InvalidIntegrationSignatureError",
    "NoUsableCredentialError",
    "ReplayDetectedError",
    "ReplayProtectionError",
    "ReplayProtector",
    "TimestampOutsideToleranceError",
)
