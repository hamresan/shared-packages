from dataclasses import replace
from datetime import UTC, datetime

import pytest

from identity.application.errors import (
    InvalidOtpError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
    OtpExpiredError,
)
from identity.application.verifiers import OtpChallengeVerifier
from identity.domain import OtpPurpose
from tests.support.hmac import build_hmac_hasher
from tests.support.otp import build_otp_challenge

TEST_SECRET = b"otp-verification-test-secret-32b!"


def test_verifier_returns_valid_challenge() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = build_otp_challenge(
        purpose=OtpPurpose.LOGIN,
        now=now,
        code_hash=hasher.hash("123456"),
    )

    result = OtpChallengeVerifier(hasher).verify(
        challenge=challenge,
        code="123456",
        now=now,
    )

    assert result is challenge


def test_verifier_rejects_missing_challenge() -> None:
    verifier = OtpChallengeVerifier(build_hmac_hasher(TEST_SECRET))

    with pytest.raises(OtpChallengeNotFoundError):
        verifier.verify(challenge=None, code="123456", now=datetime.now(UTC))


def test_verifier_rejects_expired_challenge() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = build_otp_challenge(
        purpose=OtpPurpose.LOGIN,
        now=now,
        code_hash=hasher.hash("123456"),
    )
    expired = replace(challenge, expires_at=now)

    with pytest.raises(OtpExpiredError):
        OtpChallengeVerifier(hasher).verify(
            challenge=expired,
            code="123456",
            now=now,
        )


def test_verifier_rejects_exhausted_attempts() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = build_otp_challenge(
        purpose=OtpPurpose.LOGIN,
        now=now,
        code_hash=hasher.hash("123456"),
    )
    exhausted = replace(challenge, attempts_count=challenge.max_attempts)

    with pytest.raises(OtpAttemptsExceededError):
        OtpChallengeVerifier(hasher).verify(
            challenge=exhausted,
            code="123456",
            now=now,
        )


def test_verifier_rejects_invalid_code() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = build_otp_challenge(
        purpose=OtpPurpose.LOGIN,
        now=now,
        code_hash=hasher.hash("123456"),
    )

    with pytest.raises(InvalidOtpError):
        OtpChallengeVerifier(hasher).verify(
            challenge=challenge,
            code="654321",
            now=now,
        )
