"""Application errors for Instagram comment reads."""


class InstagramCommentAccessError(Exception):
    """Base error for comment read access."""


class InstagramCommentConnectionUnavailableError(InstagramCommentAccessError):
    """Selected connection cannot currently read comments."""


class InstagramCommentPermissionRequiredError(InstagramCommentAccessError):
    """Selected connection lacks a required comment-read permission."""
