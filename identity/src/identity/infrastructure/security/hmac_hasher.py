import hashlib
import hmac

from identity.application.contracts.security import SecretHasher

MINIMUM_HMAC_SECRET_BYTES = 32


class HmacSha256SecretHasher(SecretHasher):
    def __init__(self, secret: bytes) -> None:
        if len(secret) < MINIMUM_HMAC_SECRET_BYTES:
            raise ValueError(f"Secret must be at least {MINIMUM_HMAC_SECRET_BYTES} bytes")
        self._secret = secret

    def hash(self, value: str) -> str:
        return hmac.new(self._secret, value.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, value: str, hashed_value: str) -> bool:
        return hmac.compare_digest(self.hash(value), hashed_value)
