"""Instagram webhook handshake tests."""

import pytest

from instagram_api.application.webhooks import (
    InstagramWebhookHandshakeError,
    InstagramWebhookHandshakeService,
)


def test_handshake_returns_challenge_for_valid_subscription() -> None:
    service = InstagramWebhookHandshakeService("verify-secret")

    challenge = service.verify(
        mode="subscribe",
        verify_token="verify-secret",
        challenge="challenge-value",
    )

    assert challenge == "challenge-value"


@pytest.mark.parametrize(
    ("mode", "verify_token", "challenge"),
    [
        ("invalid", "verify-secret", "challenge"),
        ("subscribe", "wrong", "challenge"),
        ("subscribe", "verify-secret", None),
    ],
)
def test_handshake_rejects_invalid_requests(
    mode: str | None,
    verify_token: str | None,
    challenge: str | None,
) -> None:
    service = InstagramWebhookHandshakeService("verify-secret")

    with pytest.raises(InstagramWebhookHandshakeError):
        service.verify(
            mode=mode,
            verify_token=verify_token,
            challenge=challenge,
        )
