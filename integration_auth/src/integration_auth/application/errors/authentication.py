"""Application authentication errors."""


class IntegrationAuthenticationError(Exception):
    """Base error for integration request authentication failures."""


class IntegrationClientNotFoundError(IntegrationAuthenticationError):
    """Raised when no integration client matches the supplied identifier."""


class NoUsableCredentialError(IntegrationAuthenticationError):
    """Raised when a client has no credential eligible for authentication."""


class InvalidIntegrationSignatureError(IntegrationAuthenticationError):
    """Raised when no usable credential verifies the request signature."""
