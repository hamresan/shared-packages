import hashlib
import hmac


class HmacSha256DigestCalculator:
    def calculate(self, secret: bytes, value: str) -> str:
        return hmac.new(secret, value.encode("utf-8"), hashlib.sha256).hexdigest()
