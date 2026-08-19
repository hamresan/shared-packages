import pytest

from identity.infrastructure.security.hmac_hasher import (
    MINIMUM_HMAC_SECRET_BYTES,
    HmacSha256SecretHasher,
)


def test_rejects_secret_shorter_than_minimum() -> None:
    with pytest.raises(ValueError, match="at least 32 bytes"):
        HmacSha256SecretHasher(b"x" * (MINIMUM_HMAC_SECRET_BYTES - 1))


def test_accepts_secret_at_minimum_length() -> None:
    hasher = HmacSha256SecretHasher(b"x" * MINIMUM_HMAC_SECRET_BYTES)

    hashed_value = hasher.hash("123456")

    assert hasher.verify("123456", hashed_value)
    assert not hasher.verify("654321", hashed_value)
