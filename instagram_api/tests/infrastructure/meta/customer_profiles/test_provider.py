"""Meta Instagram customer profile provider tests."""

import asyncio

from instagram_api.domain import InstagramConnectionId, InstagramUserId
from instagram_api.infrastructure.meta.customer_profiles import (
    CUSTOMER_PROFILE_FIELDS,
    MetaInstagramCustomerProfileMapper,
    MetaInstagramCustomerProfilePayloadParser,
    MetaInstagramCustomerProfileProvider,
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


def test_provider_reads_instagram_scoped_customer_profile() -> None:
    connection_id = InstagramConnectionId("connection")
    user_id = InstagramUserId("1234567890")
    token_provider = FakeInstagramAccessTokenProvider({connection_id: "token"})
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                b'{"id":"1234567890","username":"customer","name":"Customer",'
                b'"profile_pic":"https://example.com/profile.jpg"}',
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
    provider = MetaInstagramCustomerProfileProvider(
        executor,
        MetaInstagramCustomerProfilePayloadParser(),
        MetaInstagramCustomerProfileMapper(),
    )

    profile = asyncio.run(provider.get_customer_profile(connection_id, user_id))

    assert profile.id == user_id
    assert profile.username == "customer"
    assert profile.name == "Customer"
    assert profile.profile_picture_url == "https://example.com/profile.jpg"
    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request.method is MetaHttpMethod.GET
    assert request.url.endswith("/v24.0/1234567890")
    assert request.params["fields"] == ",".join(CUSTOMER_PROFILE_FIELDS)
    assert request.headers["Authorization"] == "Bearer token"
