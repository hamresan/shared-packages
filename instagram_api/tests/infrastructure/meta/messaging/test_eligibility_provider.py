"""Meta outbound recipient eligibility tests."""

import asyncio

from instagram_api.domain import InstagramConnectionId, InstagramUserId
from instagram_api.infrastructure.meta.http import MetaHttpResponse
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport
from tests.infrastructure.meta.messaging.outbound_factories import (
    build_eligibility_checker,
)


def test_eligibility_checker_finds_existing_recipient_conversation() -> None:
    connection_id = InstagramConnectionId("connection")
    recipient_id = InstagramUserId("recipient")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                b'{"data":[{"id":"conversation","updated_time":"2026-09-04T10:00:00+0000"}]}',
            )
        ]
    )
    checker = build_eligibility_checker(transport, connection_id)

    eligible = asyncio.run(checker.is_eligible(connection_id, recipient_id))

    assert eligible is True
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/me/conversations")
    assert request.params == {"user_id": "recipient"}
    assert request.headers["Authorization"] == "Bearer token"


def test_eligibility_checker_returns_false_when_no_conversation_exists() -> None:
    connection_id = InstagramConnectionId("connection")
    recipient_id = InstagramUserId("recipient")
    transport = SequenceMetaHttpTransport([MetaHttpResponse(200, {}, b'{"data":[]}')])
    checker = build_eligibility_checker(transport, connection_id)

    assert asyncio.run(checker.is_eligible(connection_id, recipient_id)) is False
