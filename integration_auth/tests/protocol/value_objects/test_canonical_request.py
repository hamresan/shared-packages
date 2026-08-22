import pytest

from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


def test_canonical_request_preserves_validated_values() -> None:
    request = CanonicalRequest(
        method="GET",
        path="/items",
        canonical_query="a=1",
        timestamp=10,
        nonce="nonce-1",
        body_sha256="0" * 64,
    )

    assert request.method == "GET"
    assert request.path == "/items"
    assert request.canonical_query == "a=1"
    assert request.timestamp == 10


def test_canonical_request_rejects_noncanonical_method() -> None:
    with pytest.raises(ValueError, match="method"):
        CanonicalRequest(
            method="get",
            path="/items",
            canonical_query="",
            timestamp=10,
            nonce="nonce-1",
            body_sha256="0" * 64,
        )
