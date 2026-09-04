"""Application errors for Instagram webhook processing."""


class InstagramWebhookError(Exception):
    """Base error for Instagram webhook processing."""


class InstagramWebhookAuthenticationError(InstagramWebhookError):
    """Webhook request failed authenticity validation."""


class InstagramWebhookHandshakeError(InstagramWebhookError):
    """Webhook verification handshake is invalid."""
