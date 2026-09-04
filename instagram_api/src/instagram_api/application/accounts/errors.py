"""Application errors for Instagram account access."""


class InstagramAccountAccessError(Exception):
    """Base error for selected Instagram account access."""


class InstagramConnectionUnavailableError(InstagramAccountAccessError):
    """Selected Instagram connection is not usable."""


class InstagramPermissionRequiredError(InstagramAccountAccessError):
    """Selected Instagram connection lacks a required permission."""


class InstagramAccountMismatchError(InstagramAccountAccessError):
    """Provider account does not match the selected connection."""
