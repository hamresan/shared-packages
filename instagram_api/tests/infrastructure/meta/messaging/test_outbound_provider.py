"""Meta Send API provider tests."""

import asyncio

import pytest

from instagram_api.application.messaging import InstagramMessageSendRejectedError
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMessageId,
    InstagramMessageSendRequest,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaHttpResponse, MetaTransientError
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport
from tests.infrastructure.meta.messaging.outbound_factories import build_outbound_provider


def test_outbound_provider_posts_text_message_and_parses_result() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                b'{"recipient_id":"recipient","message_id":"message"}',
            )
        ]
    )
    provider = build_outbound_provider(transport, connection_id)

    result = asyncio.run(
        provider.send_message(
            connection_id,
            InstagramMessageSendRequest(
                InstagramUserId("recipient"),
                text="hello",
                correlation_id="not-sent-to-meta",
            ),
        )
    )

    assert result.message_id == InstagramMessageId("message")
    assert result.recipient_id == InstagramUserId("recipient")
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/me/messages")
    assert request.json_body == {
        "recipient": {"id": "recipient"},
        "message": {"text": "hello"},
    }


def test_outbound_provider_normalizes_provider_rejection() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                400,
                {},
                b'{"error":{"message":"Recipient is not eligible","code":10}}',
            )
        ]
    )
    provider = build_outbound_provider(transport, connection_id)

    with pytest.raises(InstagramMessageSendRejectedError):
        asyncio.run(
            provider.send_message(
                connection_id,
                InstagramMessageSendRequest(
                    InstagramUserId("recipient"),
                    text="hello",
                ),
            )
        )


def test_outbound_provider_does_not_retry_non_idempotent_post() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                500,
                {},
                b'{"error":{"message":"temporary","code":2}}',
            ),
            MetaHttpResponse(
                200,
                {},
                b'{"recipient_id":"recipient","message_id":"duplicate-risk"}',
            ),
        ]
    )
    provider = build_outbound_provider(transport, connection_id)

    with pytest.raises(MetaTransientError):
        asyncio.run(
            provider.send_message(
                connection_id,
                InstagramMessageSendRequest(
                    InstagramUserId("recipient"),
                    text="hello",
                ),
            )
        )

    assert len(transport.requests) == 1
