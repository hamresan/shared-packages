from collections.abc import Mapping
from dataclasses import dataclass

MINIMUM_HMAC_SECRET_BYTES = 32
_KEY_ID_SEPARATOR = "$"


@dataclass(frozen=True, slots=True)
class HmacKey:
    key_id: str
    secret: bytes


class HmacKeyring:
    def __init__(
        self,
        current_key: HmacKey,
        previous_keys: Mapping[str, bytes] | None = None,
    ) -> None:
        self._validate(current_key.key_id, current_key.secret)
        previous = dict(previous_keys or {})
        if current_key.key_id in previous:
            raise ValueError("Current HMAC key id must not appear in previous secrets")

        for key_id, secret in previous.items():
            self._validate(key_id, secret)

        self._current = current_key
        self._verification_keys = (
            current_key,
            *(HmacKey(key_id=key_id, secret=secret) for key_id, secret in previous.items()),
        )

    @property
    def current(self) -> HmacKey:
        return self._current

    @property
    def verification_keys(self) -> tuple[HmacKey, ...]:
        return self._verification_keys

    def get(self, key_id: str) -> HmacKey | None:
        return next(
            (key for key in self._verification_keys if key.key_id == key_id),
            None,
        )

    def _validate(self, key_id: str, secret: bytes) -> None:
        if not key_id or _KEY_ID_SEPARATOR in key_id:
            raise ValueError("HMAC key id must be non-empty and must not contain '$'")
        if len(secret) < MINIMUM_HMAC_SECRET_BYTES:
            raise ValueError(f"Secret must be at least {MINIMUM_HMAC_SECRET_BYTES} bytes")
