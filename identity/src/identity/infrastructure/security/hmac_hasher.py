import hashlib
import hmac
from collections.abc import Mapping

from identity.application.contracts.security import SecretHasher

MINIMUM_HMAC_SECRET_BYTES = 32
_HASH_FORMAT = "hmac-sha256"
_HASH_SEPARATOR = "$"


class HmacSha256SecretHasher(SecretHasher):
    def __init__(
        self,
        secret: bytes,
        *,
        key_id: str = "v1",
        previous_secrets: Mapping[str, bytes] | None = None,
    ) -> None:
        self._validate_key(key_id, secret)
        previous = dict(previous_secrets or {})
        if key_id in previous:
            raise ValueError("Current HMAC key id must not appear in previous secrets")
        for previous_key_id, previous_secret in previous.items():
            self._validate_key(previous_key_id, previous_secret)

        self._current_key_id = key_id
        self._current_secret = secret
        self._verification_secrets = {key_id: secret, **previous}

    def hash(self, value: str) -> str:
        digest = self._digest(self._current_secret, value)
        return self._format_versioned_hash(self._current_key_id, digest)

    def hash_candidates(self, value: str) -> tuple[str, ...]:
        versioned = tuple(
            self._format_versioned_hash(key_id, self._digest(secret, value))
            for key_id, secret in self._verification_secrets.items()
        )
        legacy = tuple(
            self._digest(secret, value) for secret in self._verification_secrets.values()
        )
        return versioned + legacy

    def verify(self, value: str, hashed_value: str) -> bool:
        parsed = self._parse_versioned_hash(hashed_value)
        if parsed is not None:
            key_id, stored_digest = parsed
            secret = self._verification_secrets.get(key_id)
            if secret is None:
                return False
            return hmac.compare_digest(self._digest(secret, value), stored_digest)

        return any(
            hmac.compare_digest(self._digest(secret, value), hashed_value)
            for secret in self._verification_secrets.values()
        )

    @staticmethod
    def _digest(secret: bytes, value: str) -> str:
        return hmac.new(secret, value.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def _format_versioned_hash(key_id: str, digest: str) -> str:
        return _HASH_SEPARATOR.join((_HASH_FORMAT, key_id, digest))

    @staticmethod
    def _parse_versioned_hash(hashed_value: str) -> tuple[str, str] | None:
        parts = hashed_value.split(_HASH_SEPARATOR, 2)
        if len(parts) != 3 or parts[0] != _HASH_FORMAT:
            return None
        key_id, digest = parts[1], parts[2]
        if not key_id or not digest:
            return None
        return key_id, digest

    @staticmethod
    def _validate_key(key_id: str, secret: bytes) -> None:
        if not key_id or _HASH_SEPARATOR in key_id:
            raise ValueError("HMAC key id must be non-empty and must not contain '$'")
        if len(secret) < MINIMUM_HMAC_SECRET_BYTES:
            raise ValueError(f"Secret must be at least {MINIMUM_HMAC_SECRET_BYTES} bytes")
