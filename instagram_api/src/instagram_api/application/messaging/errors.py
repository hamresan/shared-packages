"""Application errors for Instagram messaging reads."""


class InstagramMessagingAccessError(Exception):
    """Base error for conversation/message access."""


class InstagramMessagingConnectionUnavailableError(InstagramMessagingAccessError):
    """Selected Instagram connection is not usable."""


class InstagramMessagingPermissionRequiredError(InstagramMessagingAccessError):
    """Selected connection lacks a required messaging permission."""
