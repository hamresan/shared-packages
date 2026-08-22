"""Application error public API."""

from integration_auth.application.errors.authentication import (
    IntegrationAuthenticationError,
    IntegrationClientNotFoundError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
)
from integration_auth.application.errors.replay import (
    ReplayDetectedError,
    ReplayProtectionError,
    TimestampOutsideToleranceError,
)

__all__ = (
    "IntegrationAuthenticationError",
    "IntegrationClientNotFoundError",
    "InvalidIntegrationSignatureError",
    "NoUsableCredentialError",
    "ReplayDetectedError",
    "ReplayProtectionError",
    "TimestampOutsideToleranceError",
)
