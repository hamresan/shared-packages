"""Instagram webhook verification handshake use case."""

from .errors import InstagramWebhookHandshakeError


class InstagramWebhookHandshakeService:
    """Validates Meta webhook verification challenges."""

    def __init__(self, verify_token: str) -> None:
        self._verify_token = verify_token

    def verify(
        self,
        *,
        mode: str | None,
        verify_token: str | None,
        challenge: str | None,
    ) -> str:
        """Return the challenge only for a valid subscribe handshake."""

        if mode != "subscribe":
            raise InstagramWebhookHandshakeError(
                "Webhook verification mode must be subscribe."
            )
        if verify_token != self._verify_token:
            raise InstagramWebhookHandshakeError(
                "Webhook verification token is invalid."
            )
        if challenge is None or not challenge:
            raise InstagramWebhookHandshakeError(
                "Webhook verification challenge is missing."
            )
        return challenge
