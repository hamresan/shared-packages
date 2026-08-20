import hmac

from identity.application.contracts.security import SecretHasher
from identity.infrastructure.security.hmac_digest import HmacSha256DigestCalculator
from identity.infrastructure.security.hmac_hash_format import HmacHashFormat
from identity.infrastructure.security.hmac_keyring import HmacKeyring


class HmacSha256SecretHasher(SecretHasher):
    def __init__(
        self,
        *,
        keyring: HmacKeyring,
        digest_calculator: HmacSha256DigestCalculator,
        hash_format: HmacHashFormat,
    ) -> None:
        self._keyring = keyring
        self._digest_calculator = digest_calculator
        self._hash_format = hash_format

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
