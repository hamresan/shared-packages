from tests.support.infrastructure.crypto.hmac_verifier_factory import HmacVerifierFactory
from tests.support.protocol.canonical_request_builder import CanonicalRequestBuilder
from tests.support.protocol.known_answer_vector import EXPECTED_SIGNATURE, TEST_SECRET


def test_accepts_matching_signature() -> None:
    assert HmacVerifierFactory().build().verify(
        CanonicalRequestBuilder().build(),
        TEST_SECRET,
        EXPECTED_SIGNATURE,
    )


def test_rejects_invalid_signature() -> None:
    assert not HmacVerifierFactory().build().verify(
        CanonicalRequestBuilder().build(),
        TEST_SECRET,
        "0" * 64,
    )


def test_rejects_signature_when_path_changes() -> None:
    builder = CanonicalRequestBuilder()
    builder.path = "/api/catalog/other"

    assert not HmacVerifierFactory().build().verify(
        builder.build(), TEST_SECRET, EXPECTED_SIGNATURE
    )


def test_rejects_signature_when_query_changes() -> None:
    builder = CanonicalRequestBuilder()
    builder.canonical_query = "page=3"

    assert not HmacVerifierFactory().build().verify(
        builder.build(), TEST_SECRET, EXPECTED_SIGNATURE
    )


def test_rejects_signature_when_timestamp_changes() -> None:
    builder = CanonicalRequestBuilder()
    builder.timestamp += 1

    assert not HmacVerifierFactory().build().verify(
        builder.build(), TEST_SECRET, EXPECTED_SIGNATURE
    )


def test_rejects_signature_when_body_hash_changes() -> None:
    builder = CanonicalRequestBuilder()
    builder.body_sha256 = "0" * 64

    assert not HmacVerifierFactory().build().verify(
        builder.build(), TEST_SECRET, EXPECTED_SIGNATURE
    )
