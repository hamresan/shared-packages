import pytest

from integration_auth.application.contracts.crypto.request_signer import RequestSigner
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_signer import HmacSha256RequestSigner
from integration_auth.protocol.canonicalization.canonical_request_serializer import CanonicalRequestSerializer
from tests.support.protocol.canonical_request_builder import CanonicalRequestBuilder
from tests.support.protocol.known_answer_vector import EXPECTED_SIGNATURE, TEST_SECRET


def test_signs_known_answer_vector() -> None:
    signer: RequestSigner = HmacSha256RequestSigner(CanonicalRequestSerializer())

    assert signer.sign(CanonicalRequestBuilder().build(), TEST_SECRET) == EXPECTED_SIGNATURE


def test_rejects_empty_hmac_secret() -> None:
    signer = HmacSha256RequestSigner(CanonicalRequestSerializer())

    with pytest.raises(ValueError, match="must not be empty"):
        signer.sign(CanonicalRequestBuilder().build(), b"")
