import hmac
from collections.abc import Mapping

from identity.application.contracts.security import SecretHasher
from identity.infrastructure.security.hmac_digest import HmacSha256DigestCalculator
from identity.infrastructure.security.hmac_hash_format import HmacHashFormat
from identity.infrastructure.security.hmac_key_validator import MINIMUM_HMAC_SECRET_BYTES
from identity.infrastructure.security.hmac_keyring import HmacKey, HmacKeyring


class HmacSha256SecretHasher(SecretHasher):
    def __init__(
        self,
        secret: bytes,
        *,
        key_id: str = "v1",
        previous_secrets: Mapping[str, bytes] | None = None,
        digest_calculator: HmacSha256DigestCalculator | None = None,
        hash_format: HmacHashFormat | None = None,
        keyring: HmacKeyring | None = None,
    ) -> None:
        self._digest_calculator = digest_calculator or HmacSha256DigestCalculator()
        self._hash_format = hash_format or HmacHashFormat()
        self._keyring = keyring or HmacKeyring(
            current_key=HmacKey(key_id=key_id, secret=secret),
            previous_keys=previous_secrets,
        )

    def hash(self, value: str) -> str:
        current_key = self._keyring.current
        digest = self._digest_calculator.calculate(current_key.secret, value)
        return self._hash_format.format(current_key.key_id, digest)

    def hash_candidates(self, value: str) -> tuple[str, ...]:
        versioned = tuple(
            self._hash_format.format(
                key.key_id,
                self._digest_calculator.calculate(key.secret, value),
            )
            for key in self._keyring.verification_keys
        )
        legacy = tuple(
            self._digest_calculator.calculate(key.secret, value)
            for key in self._keyring.verification_keys
        )
        return versioned + legacy

    def verify(self, value: str, hashed_value: str) -> bool:
        parsed = self._hash_format.parse(hashed_value)
        if parsed is not None:
            key = self._keyring.get(parsed.key_id)
            if key is None:
                return False
            digest = self._digest_calculator.calculate(key.secret, value)
            return hmac.compare_digest(digest, parsed.digest)

        return any(
            hmac.compare_digest(
                self._digest_calculator.calculate(key.secret, value),
                hashed_value,
            )
            for key in self._keyring.verification_keys
        )
