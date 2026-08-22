"""Executable Python known-answer interoperability example."""

from __future__ import annotations

import json
from pathlib import Path

from integration_auth.infrastructure.crypto.hashing.sha256_body_hasher import Sha256BodyHasher
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_signer import (
    HmacSha256RequestSigner,
)
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_verifier import (
    HmacSha256RequestVerifier,
)
from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder
from integration_auth.protocol.canonicalization.canonical_request_serializer import (
    CanonicalRequestSerializer,
)
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest

VECTORS_PATH = Path(__file__).with_name("vectors.json")


def main() -> None:
    vectors = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    encoder = CanonicalQueryEncoder()
    hasher = Sha256BodyHasher()
    serializer = CanonicalRequestSerializer()
    signer = HmacSha256RequestSigner(serializer)
    verifier = HmacSha256RequestVerifier(serializer)

    results: dict[str, bool] = {}
    for name in ("inbound", "outbound"):
        vector = vectors[name]
        body = vector["body"].encode("utf-8")
        canonical_query = encoder.encode([tuple(item) for item in vector["query"]])
        request = CanonicalRequest(
            method=vector["method"],
            path=vector["path"],
            canonical_query=canonical_query,
            timestamp=vector["timestamp"],
            nonce=vector["nonce"],
            body_sha256=hasher.hash(body),
        )
        signature = signer.sign(request, vector["secret"].encode("utf-8"))
        results[name] = (
            canonical_query == vector["canonical_query"]
            and request.body_sha256 == vector["body_sha256"]
            and signature == vector["signature"]
            and verifier.verify(request, vector["secret"].encode("utf-8"), signature)
        )

    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
