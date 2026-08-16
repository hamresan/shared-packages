import hashlib
import hmac

from identity.application.contracts.security import SecretHasher


class HmacSha256SecretHasher(SecretHasher):
    def __init__(self, secret: bytes) -> None:
        if not secret:
            raise ValueError("Secret must not be empty")
        self._secret = secret

    def hash(self, value: str) -> str:
        return hmac.new(self._secret, value.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, value: str, hashed_value: str) -> bool:
        return hmac.compare_digest(self.hash(value), hashed_value)
