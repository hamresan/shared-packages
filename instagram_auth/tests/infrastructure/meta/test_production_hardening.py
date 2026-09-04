"""Production hardening tests for the Meta provider boundary."""

from asyncio import run

import pytest

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.client import MetaInstagramOAuthClient
from instagram_auth.infrastructure.meta.config import MetaInstagramOAuthConfig
from instagram_auth.infrastructure.meta.http import MetaHttpResponse, MetaTransportTimeoutError
from instagram_auth.infrastructure.meta.mappers import MetaProviderErrorMapper
from instagram_auth.infrastructure.meta.parsers import (
    MetaIdentityPayloadParser,
    MetaTokenPayloadParser,
)
from instagram_auth.infrastructure.meta.retry import MetaIdentityRetryPolicy
from tests.infrastructure.meta.fakes import FakeMetaHttpTransport


def build_client(transport: FakeMetaHttpTransport) -> MetaInstagramOAuthClient:
    return MetaInstagramOAuthClient(
        transport=transport,
        config=MetaInstagramOAuthConfig(
            client_id="client-id",
            client_secret="client-secret",
            graph_api_version="v25.0",
        ),
        error_mapper=MetaProviderErrorMapper(),
        token_parser=MetaTokenPayloadParser(),
        identity_parser=MetaIdentityPayloadParser(),
        identity_retry_policy=MetaIdentityRetryPolicy(max_attempts=2),
    )


def test_token_exchange_does_not_retry_transient_provider_failure() -> None:
    transport = FakeMetaHttpTransport()
    transport.post_results.extend(
        [
            MetaHttpResponse(503, {"error": "temporary", "secret": "provider-payload-secret"}),
            MetaHttpResponse(200, {"access_token": "must-not-be-used"}),
        ]
    )

    with pytest.raises(InstagramProviderError) as exc_info:
        run(
            build_client(transport).exchange_authorization_code(
                authorization_code="sensitive-code",
                redirect_uri="https://app.example/callback",
            )
        )

    assert exc_info.value.kind is InstagramProviderErrorKind.PROVIDER_UNAVAILABLE
    assert exc_info.value.status_code == 503
    assert "sensitive-code" not in str(exc_info.value)
    assert "provider-payload-secret" not in str(exc_info.value)
    assert len(transport.post_calls) == 1


def test_identity_retry_exhaustion_returns_structured_safe_error() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.extend([MetaHttpResponse(503, {}), MetaHttpResponse(503, {})])

    with pytest.raises(InstagramProviderError) as exc_info:
        run(build_client(transport).resolve_identity(access_token="sensitive-token"))

    assert exc_info.value.kind is InstagramProviderErrorKind.PROVIDER_UNAVAILABLE
    assert exc_info.value.status_code == 503
    assert "sensitive-token" not in str(exc_info.value)
    assert len(transport.get_calls) == 2


def test_identity_timeout_exhaustion_masks_transport_details() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.extend(
        [
            MetaTransportTimeoutError("first sensitive timeout"),
            MetaTransportTimeoutError("second sensitive timeout"),
        ]
    )

    with pytest.raises(InstagramProviderError) as exc_info:
        run(build_client(transport).resolve_identity(access_token="sensitive-token"))

    assert exc_info.value.kind is InstagramProviderErrorKind.TIMEOUT
    assert "sensitive-token" not in str(exc_info.value)
    assert "sensitive timeout" not in str(exc_info.value)


def test_rate_limit_error_is_structured_without_provider_payload() -> None:
    secret_payload_value = "provider-secret-value"
    error = MetaProviderErrorMapper().identity_error(
        MetaHttpResponse(429, {"error": secret_payload_value})
    )

    assert error.kind is InstagramProviderErrorKind.RATE_LIMITED
    assert error.status_code == 429
    assert secret_payload_value not in str(error)
