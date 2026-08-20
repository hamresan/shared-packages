from collections.abc import Mapping
from dataclasses import dataclass

from identity.infrastructure.security.hmac_key_validator import HmacKeyValidator


@dataclass(frozen=True, slots=True)
class HmacKey:
    key_id: str
    secret: bytes


class HmacKeyring:
    def __init__(
        self,
        current_key: HmacKey,
        previous_keys: Mapping[str, bytes] | None = None,
        validator: HmacKeyValidator | None = None,
    ) -> None:
        key_validator = validator or HmacKeyValidator()
        key_validator.validate(current_key.key_id, current_key.secret)

        previous = dict(previous_keys or {})
        if current_key.key_id in previous:
            raise ValueError("Current HMAC key id must not appear in previous secrets")

        for key_id, secret in previous.items():
            key_validator.validate(key_id, secret)

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
