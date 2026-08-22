"""Public application API for integration-auth."""

from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.application.dto.authorization import (
    AuthorizationDecisionReason,
    AuthorizationResult,
)
from integration_auth.application.dto.provisioning import IssuedCredential
from integration_auth.application.errors import (
    IntegrationAuthenticationError,
    IntegrationAuthorizationError,
    IntegrationClientNotFoundError,
    IntegrationProvisioningError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
    ProvisioningClientNotFoundError,
    ProvisioningCredentialNotFoundError,
    ReplayDetectedError,
    ReplayProtectionError,
    TimestampOutsideToleranceError,
)
from integration_auth.application.services import (
    AuthenticateIntegrationRequestService,
    ExpireCredentialService,
    IntegrationAuthorizer,
    IssueCredentialService,
    RegisterIntegrationClientService,
    ReplayProtector,
    RevokeCredentialService,
    RotateCredentialService,
    UpdateIntegrationClientGrantsService,
)

__all__ = (
    "AuthenticateIntegrationRequest",
    "AuthenticateIntegrationRequestService",
    "AuthorizationDecisionReason",
    "AuthorizationResult",
    "ExpireCredentialService",
    "IntegrationAuthenticationError",
    "IntegrationAuthorizationError",
    "IntegrationAuthorizer",
    "IntegrationClientNotFoundError",
    "IntegrationProvisioningError",
    "InvalidIntegrationSignatureError",
    "IssueCredentialService",
    "IssuedCredential",
    "NoUsableCredentialError",
    "ProvisioningClientNotFoundError",
    "ProvisioningCredentialNotFoundError",
    "RegisterIntegrationClientService",
    "ReplayDetectedError",
    "ReplayProtectionError",
    "ReplayProtector",
    "RevokeCredentialService",
    "RotateCredentialService",
    "TimestampOutsideToleranceError",
    "UpdateIntegrationClientGrantsService",
)
