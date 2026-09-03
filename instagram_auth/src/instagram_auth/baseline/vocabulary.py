"""Normalized vocabulary fixed by the Stage 0 provider capability baseline."""

from enum import StrEnum


class InstagramConnectionState(StrEnum):
    """High-level authorization lifecycle states exposed to consuming applications."""

    AUTHORIZING = "authorizing"
    CONNECTED = "connected"
    REAUTHORIZATION_REQUIRED = "reauthorization_required"
    DISCONNECTED = "disconnected"


class InstagramProviderErrorKind(StrEnum):
    """Provider-independent error categories used at the package boundary."""

    ACCESS_DENIED = "access_denied"
    INVALID_REQUEST = "invalid_request"
    INVALID_AUTHORIZATION_CODE = "invalid_authorization_code"
    INVALID_TOKEN = "invalid_token"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    UNEXPECTED_PROVIDER_ERROR = "unexpected_provider_error"
