from collections.abc import Mapping

from identity.infrastructure.security.hmac_digest import HmacSha256DigestCalculator
from identity.infrastructure.security.hmac_hash_format import HmacHashFormat
from identity.infrastructure.security.hmac_hasher import HmacSha256SecretHasher
from identity.infrastructure.security.hmac_key_validator import HmacKeyValidator
from identity.infrastructure.security.hmac_keyring import HmacKey, HmacKeyring


def build_hmac_hasher(
    secret: bytes,
    *,
    key_id: str = "v1",
    previous_secrets: Mapping[str, bytes] | None = None,
) -> HmacSha256SecretHasher:
    keyring = HmacKeyring(
        current_key=HmacKey(key_id=key_id, secret=secret),
        previous_keys=previous_secrets or {},
        validator=HmacKeyValidator(),
    )
    return HmacSha256SecretHasher(
        keyring=keyring,
        digest_calculator=HmacSha256DigestCalculator(),
        hash_format=HmacHashFormat(),
    )
