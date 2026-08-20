import hashlib
import hmac

import pytest

from identity.infrastructure.security.hmac_hasher import (
    MINIMUM_HMAC_SECRET_BYTES,
    HmacSha256SecretHasher,
)

CURRENT_SECRET = b"c" * MINIMUM_HMAC_SECRET_BYTES
PREVIOUS_SECRET = b"p" * MINIMUM_HMAC_SECRET_BYTES


def test_rejects_secret_shorter_than_minimum() -> None:
    with pytest.raises(ValueError, match="at least 32 bytes"):
        HmacSha256SecretHasher(b"x" * (MINIMUM_HMAC_SECRET_BYTES - 1))


def test_accepts_secret_at_minimum_length() -> None:
    hasher = HmacSha256SecretHasher(CURRENT_SECRET)

    hashed_value = hasher.hash("123456")

    assert hashed_value.startswith("hmac-sha256$v1$")
    assert hasher.verify("123456", hashed_value)
    assert not hasher.verify("654321", hashed_value)


def test_writes_with_current_key_and_verifies_previous_key() -> None:
    previous_hasher = HmacSha256SecretHasher(PREVIOUS_SECRET, key_id="2026-07")
    previous_hash = previous_hasher.hash("refresh-token")
    rotated_hasher = HmacSha256SecretHasher(
        CURRENT_SECRET,
        key_id="2026-08",
        previous_secrets={"2026-07": PREVIOUS_SECRET},
    )

    current_hash = rotated_hasher.hash("refresh-token")
    candidates = rotated_hasher.hash_candidates("refresh-token")

    assert current_hash.startswith("hmac-sha256$2026-08$")
    assert current_hash in candidates
    assert previous_hash in candidates
    assert len(candidates) == 4
    assert rotated_hasher.verify("refresh-token", previous_hash)
    assert rotated_hasher.verify("refresh-token", current_hash)


def test_rejects_versioned_hash_for_unknown_key() -> None:
    old_hasher = HmacSha256SecretHasher(PREVIOUS_SECRET, key_id="retired")
    retired_hash = old_hasher.hash("123456")
    current_hasher = HmacSha256SecretHasher(CURRENT_SECRET, key_id="current")

    assert not current_hasher.verify("123456", retired_hash)


def test_verifies_legacy_unversioned_hash_with_active_keys() -> None:
    legacy_hash = hmac.new(
        PREVIOUS_SECRET,
        b"legacy-token",
        hashlib.sha256,
    ).hexdigest()
    hasher = HmacSha256SecretHasher(
        CURRENT_SECRET,
        key_id="current",
        previous_secrets={"previous": PREVIOUS_SECRET},
    )

    assert legacy_hash in hasher.hash_candidates("legacy-token")
    assert hasher.verify("legacy-token", legacy_hash)
    assert not hasher.verify("wrong-token", legacy_hash)


def test_rejects_invalid_key_configuration() -> None:
    with pytest.raises(ValueError, match="key id"):
        HmacSha256SecretHasher(CURRENT_SECRET, key_id="")

    with pytest.raises(ValueError, match="key id"):
        HmacSha256SecretHasher(CURRENT_SECRET, key_id="bad$id")

    with pytest.raises(ValueError, match="must not appear"):
        HmacSha256SecretHasher(
            CURRENT_SECRET,
            key_id="current",
            previous_secrets={"current": PREVIOUS_SECRET},
        )

    with pytest.raises(ValueError, match="at least 32 bytes"):
        HmacSha256SecretHasher(
            CURRENT_SECRET,
            previous_secrets={"old": b"short"},
        )
