"""Instagram webhook verification handshake use case."""


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
            raise ValueError("Webhook verification mode must be subscribe.")
        if verify_token != self._verify_token:
            raise ValueError("Webhook verification token is invalid.")
        if challenge is None or not challenge:
            raise ValueError("Webhook verification challenge is missing.")
        return challenge
