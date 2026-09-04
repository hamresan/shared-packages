"""Application errors for Instagram comment reply operations."""


class InstagramCommentReplyError(Exception):
    """Base error for Instagram comment reply operations."""


class InstagramCommentReplyPayloadInvalidError(InstagramCommentReplyError):
    """Reply payload is invalid."""


class InstagramPrivateReplyExpiredError(InstagramCommentReplyError):
    """Private reply is outside Meta's documented eligibility window."""


class InstagramPrivateReplyLiveInactiveError(InstagramCommentReplyError):
    """Private reply targets an Instagram Live comment after the broadcast ended."""


class InstagramPrivateReplyIneligibleError(InstagramCommentReplyError):
    """Provider rejected a private reply under current eligibility rules."""


class InstagramPublicReplyRejectedError(InstagramCommentReplyError):
    """Provider rejected a public comment reply."""
