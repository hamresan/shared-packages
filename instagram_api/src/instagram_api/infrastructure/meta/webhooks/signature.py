"""Meta webhook signature verification."""

import hashlib
import hmac

from instagram_api.application.contracts.webhooks import InstagramWebhookVerifier


class MetaInstagramWebhookSignatureVerifier(InstagramWebhookVerifier):
    """Verifies Meta X-Hub-Signature-256 values with the app secret."""

    _PREFIX = "sha256="

    def __init__(self, app_secret: str) -> None:
        self._secret = app_secret.encode()

    def verify(self, payload: bytes, signature: str | None) -> bool:
        """Return whether signature matches the payload HMAC."""

        if signature is None or not signature.startswith(self._PREFIX):
            return False

        supplied_digest = signature.removeprefix(self._PREFIX)
        expected_digest = hmac.new(
            self._secret,
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(supplied_digest, expected_digest)
