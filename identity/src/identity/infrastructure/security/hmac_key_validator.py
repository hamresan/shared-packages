MINIMUM_HMAC_SECRET_BYTES = 32
_KEY_ID_SEPARATOR = "$"


class HmacKeyValidator:
    def validate(self, key_id: str, secret: bytes) -> None:
        if not key_id or _KEY_ID_SEPARATOR in key_id:
            raise ValueError("HMAC key id must be non-empty and must not contain '$'")
        if len(secret) < MINIMUM_HMAC_SECRET_BYTES:
            raise ValueError(f"Secret must be at least {MINIMUM_HMAC_SECRET_BYTES} bytes")
