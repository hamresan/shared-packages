"""Tests for authentication request DTO security representation."""

from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


def test_authentication_request_repr_hides_signature() -> None:
    authentication_request = AuthenticateIntegrationRequest(
        client_id=IntegrationClientId("client-123"),
        request=CanonicalRequest(
            method="GET",
            path="/protected",
            canonical_query="",
            timestamp=1_787_418_000,
            nonce="nonce-123",
            body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ),
        signature="sensitive-signature",
    )

    assert "sensitive-signature" not in repr(authentication_request)
