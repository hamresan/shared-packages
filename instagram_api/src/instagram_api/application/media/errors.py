"""Application errors for Instagram media reads."""


class InstagramMediaAccessError(Exception):
    """Base error for Instagram media access."""


class InstagramMediaConnectionUnavailableError(InstagramMediaAccessError):
    """Selected Instagram connection is not usable."""


class InstagramMediaPermissionRequiredError(InstagramMediaAccessError):
    """Selected Instagram connection lacks the required media permission."""


class InstagramMediaUnavailableError(InstagramMediaAccessError):
    """Requested Instagram media is deleted, inaccessible, or unavailable."""
