"""Meta webhook HMAC signature tests."""

import hashlib
import hmac

from instagram_api.infrastructure.meta.webhooks import (
    MetaInstagramWebhookSignatureVerifier,
)


def test_signature_verifier_accepts_valid_sha256_signature() -> None:
    payload = b'{"entry":[]}'
    secret = "app-secret"
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    verifier = MetaInstagramWebhookSignatureVerifier(secret)

    assert verifier.verify(payload, f"sha256={digest}") is True


def test_signature_verifier_rejects_missing_malformed_or_wrong_signature() -> None:
    verifier = MetaInstagramWebhookSignatureVerifier("app-secret")

    assert verifier.verify(b"payload", None) is False
    assert verifier.verify(b"payload", "sha1=bad") is False
    assert verifier.verify(b"payload", "sha256=bad") is False
