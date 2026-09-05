"""Meta Instagram account provider tests."""

import asyncio

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.accounts import (
    ACCOUNT_PROFILE_FIELDS,
    MetaInstagramAccountMapper,
    MetaInstagramAccountPayloadParser,
    MetaInstagramAccountProvider,
)
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaHttpMethod,
    MetaHttpResponse,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    NullMetaHttpObserver,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def test_provider_reads_me_with_supported_profile_fields() -> None:
    connection_id = InstagramConnectionId("connection")
    token_provider = FakeInstagramAccessTokenProvider({connection_id: "token"})
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                b'{"user_id":"account","username":"shop","biography":"Bio"}',
            )
        ]
    )
    executor = MetaRequestExecutor(
        request_builder=MetaRequestBuilder(
            MetaApiConfig(api_version="v24.0"),
            token_provider,
        ),
        transport=transport,
        decoder=MetaResponseDecoder(MetaErrorDecoder()),
        retry_policy=MetaRetryPolicy(base_delay_seconds=0),
        observer=NullMetaHttpObserver(),
    )
    provider = MetaInstagramAccountProvider(
        executor,
        MetaInstagramAccountPayloadParser(),
        MetaInstagramAccountMapper(),
    )

    account = asyncio.run(provider.get_account(connection_id))

    assert account.username == "shop"
    assert account.biography == "Bio"
    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request.method is MetaHttpMethod.GET
    assert request.url.endswith("/v24.0/me")
    assert request.params["fields"] == ",".join(ACCOUNT_PROFILE_FIELDS)
    assert request.headers["Authorization"] == "Bearer token"
