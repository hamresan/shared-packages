from asyncio import run

import pytest

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.client import MetaInstagramOAuthClient
from instagram_auth.infrastructure.meta.config import MetaInstagramOAuthConfig
from instagram_auth.infrastructure.meta.http import (
    MetaHttpResponse,
    MetaTransportError,
    MetaTransportTimeoutError,
)
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
        identity_retry_policy=MetaIdentityRetryPolicy(),
    )


def test_exchange_authorization_code_posts_expected_form_without_retry() -> None:
    transport = FakeMetaHttpTransport()
    transport.post_results.append(
        MetaHttpResponse(200, {"access_token": "token", "expires_in": 3600})
    )

    result = run(
        build_client(transport).exchange_authorization_code(
            authorization_code="code",
            redirect_uri="https://app.example/callback",
        )
    )

    assert result.access_token == "token"
    assert result.expires_in == 3600
    assert transport.post_calls == [
        (
            "https://api.instagram.com/oauth/access_token",
            {
                "client_id": "client-id",
                "client_secret": "client-secret",
                "grant_type": "authorization_code",
                "redirect_uri": "https://app.example/callback",
                "code": "code",
            },
        )
    ]


def test_exchange_authorization_code_normalizes_invalid_code() -> None:
    authorization_code = "sensitive-authorization-code-123"
    transport = FakeMetaHttpTransport()
    transport.post_results.append(MetaHttpResponse(400, {"error": "invalid"}))

    with pytest.raises(InstagramProviderError) as exc_info:
        run(
            build_client(transport).exchange_authorization_code(
                authorization_code=authorization_code,
                redirect_uri="uri",
            )
        )

    assert exc_info.value.kind is InstagramProviderErrorKind.INVALID_AUTHORIZATION_CODE
    assert authorization_code not in str(exc_info.value)
    assert len(transport.post_calls) == 1


def test_exchange_authorization_code_normalizes_timeout_without_retry() -> None:
    transport = FakeMetaHttpTransport()
    transport.post_results.append(MetaTransportTimeoutError())

    with pytest.raises(InstagramProviderError) as exc_info:
        run(
            build_client(transport).exchange_authorization_code(
                authorization_code="secret-code", redirect_uri="uri"
            )
        )

    assert exc_info.value.kind is InstagramProviderErrorKind.TIMEOUT
    assert len(transport.post_calls) == 1


def test_exchange_authorization_code_normalizes_transport_failure() -> None:
    transport = FakeMetaHttpTransport()
    transport.post_results.append(MetaTransportError())

    with pytest.raises(InstagramProviderError) as exc_info:
        run(
            build_client(transport).exchange_authorization_code(
                authorization_code="code", redirect_uri="uri"
            )
        )

    assert exc_info.value.kind is InstagramProviderErrorKind.PROVIDER_UNAVAILABLE


def test_identity_read_retries_transient_server_failure() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.extend(
        [
            MetaHttpResponse(503, {}),
            MetaHttpResponse(
                200, {"user_id": "ig-1", "username": "shop", "account_type": "BUSINESS"}
            ),
        ]
    )

    result = run(build_client(transport).resolve_identity(access_token="token"))

    assert result.user_id == "ig-1"
    assert len(transport.get_calls) == 2


def test_identity_read_retries_timeout_then_succeeds() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.extend(
        [
            MetaTransportTimeoutError(),
            MetaHttpResponse(
                200, {"user_id": "ig-1", "username": "shop", "account_type": "CREATOR"}
            ),
        ]
    )

    result = run(build_client(transport).resolve_identity(access_token="token"))

    assert result.username == "shop"
    assert len(transport.get_calls) == 2


def test_identity_read_stops_after_timeout_retry_limit() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.extend([MetaTransportTimeoutError(), MetaTransportTimeoutError()])

    with pytest.raises(InstagramProviderError) as exc_info:
        run(build_client(transport).resolve_identity(access_token="token"))

    assert exc_info.value.kind is InstagramProviderErrorKind.TIMEOUT
    assert len(transport.get_calls) == 2


def test_identity_read_normalizes_invalid_token_without_retry() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.append(MetaHttpResponse(401, {"error": "invalid"}))

    with pytest.raises(InstagramProviderError) as exc_info:
        run(build_client(transport).resolve_identity(access_token="raw-token"))

    assert exc_info.value.kind is InstagramProviderErrorKind.INVALID_TOKEN
    assert "raw-token" not in str(exc_info.value)
    assert len(transport.get_calls) == 1
