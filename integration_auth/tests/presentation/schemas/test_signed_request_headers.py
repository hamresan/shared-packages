"""Tests for signed request header schema."""

from integration_auth.presentation.schemas import SignedRequestHeaders


def test_signed_request_headers_repr_hides_signature() -> None:
    headers = SignedRequestHeaders(
        client_id="client-123",
        timestamp=1_787_418_000,
        nonce="nonce-123",
        signature="sensitive-signature",
    )

    assert "sensitive-signature" not in repr(headers)
