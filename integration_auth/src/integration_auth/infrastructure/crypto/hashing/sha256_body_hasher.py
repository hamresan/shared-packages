"""SHA-256 request body hashing."""

import hashlib

from integration_auth.application.contracts.crypto.body_hasher import BodyHasher


class Sha256BodyHasher(BodyHasher):
    """Hash request bodies as lowercase SHA-256 hexadecimal digests."""

    def hash(self, body: bytes) -> str:
        return hashlib.sha256(body).hexdigest()
