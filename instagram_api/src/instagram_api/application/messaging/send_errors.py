"""Application errors for outbound Instagram messaging."""


class InstagramMessageSendError(Exception):
    """Base outbound Instagram messaging error."""


class InstagramMessagePayloadInvalidError(InstagramMessageSendError):
    """Outbound message payload is invalid."""


class InstagramMessageRecipientIneligibleError(InstagramMessageSendError):
    """Recipient does not have an eligible existing conversation."""


class InstagramMessageSendRejectedError(InstagramMessageSendError):
    """Provider rejected the outbound message under current policy."""
