from asyncio import run
from datetime import UTC, datetime, timedelta

import pytest

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramAccountType, InstagramProviderErrorKind
from instagram_auth.infrastructure.meta import (
    MetaInstagramAuthorizationProvider,
    MetaInstagramOAuthClient,
    MetaInstagramOAuthConfig,
)
from instagram_auth.infrastructure.meta.http import MetaHttpResponse
from instagram_auth.infrastructure.meta.mappers import (
    MetaAuthorizationGrantMapper,
    MetaExternalIdentityMapper,
    MetaProviderErrorMapper,
)
from instagram_auth.infrastructure.meta.parsers import MetaIdentityPayloadParser, MetaTokenPayloadParser
from instagram_auth.infrastructure.meta.retry import MetaIdentityRetryPolicy
from tests.application.contracts.fakes import FixedClock
from tests.infrastructure.meta.fakes import FakeMetaHttpTransport

NOW = datetime(2026, 9, 3, 13, 0, tzinfo=UTC)


def build_provider(transport: FakeMetaHttpTransport) -> MetaInstagramAuthorizationProvider:
    client = MetaInstagramOAuthClient(
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
    return MetaInstagramAuthorizationProvider(
        client=client,
        grant_mapper=MetaAuthorizationGrantMapper(FixedClock(NOW)),
        identity_mapper=MetaExternalIdentityMapper(),
    )


def test_provider_maps_token_to_transient_application_grant() -> None:
    transport = FakeMetaHttpTransport()
    transport.post_results.append(MetaHttpResponse(200, {"access_token": "token", "expires_in": 3600}))

    result = run(
        build_provider(transport).exchange_authorization_code(
            authorization_code="code",
            redirect_uri="https://app.example/callback",
        )
    )

    assert result.access_token == "token"
    assert result.expires_at == NOW + timedelta(hours=1)


def test_provider_maps_professional_identity_using_user_id() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.append(
        MetaHttpResponse(
            200,
            {"user_id": "17841400000000000", "username": "shop", "account_type": "BUSINESS"},
        )
    )

    result = run(build_provider(transport).resolve_external_identity(access_token="token"))

    assert result.provider_user_id == "17841400000000000"
    assert result.username == "shop"
    assert result.account_type is InstagramAccountType.BUSINESS


def test_provider_rejects_unknown_account_type_as_normalized_error() -> None:
    transport = FakeMetaHttpTransport()
    transport.get_results.append(
        MetaHttpResponse(200, {"user_id": "ig-1", "username": "shop", "account_type": "PERSONAL"})
    )

    with pytest.raises(InstagramProviderError) as exc_info:
        run(build_provider(transport).resolve_external_identity(access_token="token"))

    assert exc_info.value.kind is InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR
