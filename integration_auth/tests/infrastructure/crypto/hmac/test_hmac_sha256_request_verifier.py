import pytest

from integration_auth.application.contracts.crypto.request_verifier import RequestVerifier
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_signer import HmacSha256RequestSigner
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_verifier import HmacSha256RequestVerifier
from integration_auth.protocol.canonicalization.canonical_request_serializer import CanonicalRequestSerializer
from tests.support.protocol.canonical_request_builder import CanonicalRequestBuilder
from tests.support.protocol.known_answer_vector import EXPECTED_SIGNATURE, TEST_SECRET


def build_verifier() -> RequestVerifier:
    signer = HmacSha256RequestSigner(CanonicalRequestSerializer())
    return HmacSha256RequestVerifier(signer)


def test_accepts_matching_signature() -> None:
    assert build_verifier().verify(
        CanonicalRequestBuilder().build(),
        TEST_SECRET,
        EXPECTED_SIGNATURE,
    )


def test_rejects_invalid_signature() -> None:
    assert not build_verifier().verify(
        CanonicalRequestBuilder().build(),
        TEST_SECRET,
        "0" * 64,
    )


@pytest.mark.parametrize("tampered_field", ["path", "canonical_query", "timestamp", "body_sha256"])
def test_rejects_signature_when_signed_request_value_changes(tampered_field: str) -> None:
    builder = CanonicalRequestBuilder()
    if tampered_field == "path":
        builder.path = "/api/catalog/other"
    elif tampered_field == "canonical_query":
        builder.canonical_query = "page=3"
    elif tampered_field == "timestamp":
        builder.timestamp += 1
    else:
        builder.body_sha256 = "0" * 64

    assert not build_verifier().verify(builder.build(), TEST_SECRET, EXPECTED_SIGNATURE)
