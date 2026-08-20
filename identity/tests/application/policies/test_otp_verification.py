from datetime import UTC, datetime, timedelta

import pytest

from identity.application.errors import (
    InvalidOtpError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
    OtpExpiredError,
)
from identity.application.factories.entities import OtpChallengeFactory
from identity.application.policies.otp_verification import OtpChallengeVerifier
from identity.domain import IdentityType, OtpPurpose
from tests.support.hmac import build_hmac_hasher

TEST_SECRET = b"otp-verification-test-secret-32b!"


def test_verifier_returns_valid_challenge() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = OtpChallengeFactory(
        ttl=timedelta(minutes=5),
        resend_delay=timedelta(seconds=60),
        max_attempts=5,
    ).create(
        now=now,
        identity_type=IdentityType.EMAIL,
        destination="user@example.com",
        purpose=OtpPurpose.LOGIN,
        code_hash=hasher.hash("123456"),
        user_id=None,
        identity_id=None,
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
    challenge = OtpChallengeFactory(
        ttl=timedelta(seconds=0),
        resend_delay=timedelta(seconds=0),
        max_attempts=5,
    ).create(
        now=now,
        identity_type=IdentityType.EMAIL,
        destination="user@example.com",
        purpose=OtpPurpose.LOGIN,
        code_hash=hasher.hash("123456"),
        user_id=None,
        identity_id=None,
    )

    with pytest.raises(OtpExpiredError):
        OtpChallengeVerifier(hasher).verify(
            challenge=challenge,
            code="123456",
            now=now,
        )


def test_verifier_rejects_exhausted_attempts() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = OtpChallengeFactory(
        ttl=timedelta(minutes=5),
        resend_delay=timedelta(seconds=60),
        max_attempts=0,
    ).create(
        now=now,
        identity_type=IdentityType.EMAIL,
        destination="user@example.com",
        purpose=OtpPurpose.LOGIN,
        code_hash=hasher.hash("123456"),
        user_id=None,
        identity_id=None,
    )

    with pytest.raises(OtpAttemptsExceededError):
        OtpChallengeVerifier(hasher).verify(
            challenge=challenge,
            code="123456",
            now=now,
        )


def test_verifier_rejects_invalid_code() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    challenge = OtpChallengeFactory(
        ttl=timedelta(minutes=5),
        resend_delay=timedelta(seconds=60),
        max_attempts=5,
    ).create(
        now=now,
        identity_type=IdentityType.EMAIL,
        destination="user@example.com",
        purpose=OtpPurpose.LOGIN,
        code_hash=hasher.hash("123456"),
        user_id=None,
        identity_id=None,
    )

    with pytest.raises(InvalidOtpError):
        OtpChallengeVerifier(hasher).verify(
            challenge=challenge,
            code="654321",
            now=now,
        )
