from dataclasses import dataclass

_HASH_FORMAT = "hmac-sha256"
_HASH_SEPARATOR = "$"


@dataclass(frozen=True, slots=True)
class ParsedHmacHash:
    key_id: str
    digest: str


class HmacHashFormat:
    def format(self, key_id: str, digest: str) -> str:
        return _HASH_SEPARATOR.join((_HASH_FORMAT, key_id, digest))

    def parse(self, hashed_value: str) -> ParsedHmacHash | None:
        parts = hashed_value.split(_HASH_SEPARATOR, 2)
        if len(parts) != 3 or parts[0] != _HASH_FORMAT:
            return None

        key_id, digest = parts[1], parts[2]
        if not key_id or not digest:
            return None

        return ParsedHmacHash(key_id=key_id, digest=digest)
