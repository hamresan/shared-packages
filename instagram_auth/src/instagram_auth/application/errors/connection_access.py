"""Connection-management access errors."""


class InstagramConnectionNotFoundError(LookupError):
    """Raised when the selected Instagram connection does not exist."""


class InstagramConnectionOwnershipError(PermissionError):
    """Raised when a host owner attempts to access another owner's connection."""
