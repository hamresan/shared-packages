from integration_auth.application.contracts.crypto.body_hasher import BodyHasher
from integration_auth.infrastructure.crypto.hashing.sha256_body_hasher import Sha256BodyHasher
from tests.support.protocol.known_answer_vector import EXPECTED_BODY_SHA256, TEST_BODY


def test_hashes_body_with_known_sha256_vector() -> None:
    hasher: BodyHasher = Sha256BodyHasher()

    assert hasher.hash(TEST_BODY) == EXPECTED_BODY_SHA256


def test_hashes_empty_body_deterministically() -> None:
    assert Sha256BodyHasher().hash(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
