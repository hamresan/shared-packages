"""Downstream Instagram access-boundary errors."""


class InstagramConnectionAccessError(RuntimeError):
    """Base error for unusable downstream Instagram connections."""


class InstagramConnectionUnavailableError(InstagramConnectionAccessError):
    """Raised when a selected connection cannot be used downstream."""


class InstagramConnectionPermissionError(InstagramConnectionAccessError):
    """Raised when a selected connection lacks required permissions."""
