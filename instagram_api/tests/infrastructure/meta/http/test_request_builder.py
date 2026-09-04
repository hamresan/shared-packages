"""Connection-aware request builder tests."""

import asyncio

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaHttpMethod,
    MetaRequestBuilder,
)
from tests.fakes import FakeInstagramAccessTokenProvider


def test_request_builder_uses_selected_connection_token_and_versioned_url() -> None:
    first = InstagramConnectionId("connection-a")
    second = InstagramConnectionId("connection-b")
    tokens = FakeInstagramAccessTokenProvider({first: "token-a", second: "token-b"})
    builder = MetaRequestBuilder(
        MetaApiConfig(api_version="v24.0"),
        tokens,
    )

    first_request = asyncio.run(
        builder.build(
            connection_id=first,
            method=MetaHttpMethod.GET,
            path="/me",
            params={"fields": "id,username"},
        )
    )
    second_request = asyncio.run(
        builder.build(
            connection_id=second,
            method=MetaHttpMethod.GET,
            path="me",
        )
    )

    assert first_request.url == "https://graph.instagram.com/v24.0/me"
    assert first_request.headers["Authorization"] == "Bearer token-a"
    assert second_request.headers["Authorization"] == "Bearer token-b"
    assert tokens.requested_connection_ids == [first, second]


def test_request_builder_fails_closed_for_unknown_connection() -> None:
    known = InstagramConnectionId("known")
    missing = InstagramConnectionId("missing")
    builder = MetaRequestBuilder(
        MetaApiConfig(api_version="v24.0"),
        FakeInstagramAccessTokenProvider({known: "token"}),
    )

    try:
        asyncio.run(
            builder.build(
                connection_id=missing,
                method=MetaHttpMethod.GET,
                path="me",
            )
        )
    except KeyError:
        pass
    else:
        raise AssertionError("Unknown connection must not fall back to another token.")
