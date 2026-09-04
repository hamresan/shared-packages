"""Outbound Instagram messaging service tests."""

import asyncio

import pytest

from instagram_api.application.messaging import (
    InstagramMessagePayloadInvalidError,
    InstagramMessagePayloadPolicy,
    InstagramMessageRecipientIneligibleError,
    InstagramMessageSendAccessPolicy,
    InstagramMessageSendService,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramMessageSendRequest,
    InstagramUserId,
)
from tests.fakes import (
    FakeInstagramConnectionReader,
    FakeInstagramMessageRecipientEligibilityChecker,
    FakeInstagramOutboundMessageProvider,
)


def build_service(
    connections: dict[InstagramConnectionId, InstagramConnection],
    eligibility: dict[tuple[InstagramConnectionId, InstagramUserId], bool],
    provider: FakeInstagramOutboundMessageProvider,
) -> InstagramMessageSendService:
    return InstagramMessageSendService(
        FakeInstagramConnectionReader(connections),
        FakeInstagramMessageRecipientEligibilityChecker(eligibility),
        provider,
        InstagramMessageSendAccessPolicy(),
        InstagramMessagePayloadPolicy(),
    )


def test_send_service_routes_two_connections_independently_and_preserves_correlation() -> None:
    first_id = InstagramConnectionId("connection-a")
    second_id = InstagramConnectionId("connection-b")
    first_recipient = InstagramUserId("recipient-a")
    second_recipient = InstagramUserId("recipient-b")
    permissions = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_messages",
        }
    )
    provider = FakeInstagramOutboundMessageProvider()
    service = build_service(
        {
            first_id: InstagramConnection(
                first_id,
                InstagramAccountId("account-a"),
                permissions,
                True,
            ),
            second_id: InstagramConnection(
                second_id,
                InstagramAccountId("account-b"),
                permissions,
                True,
            ),
        },
        {
            (first_id, first_recipient): True,
            (second_id, second_recipient): True,
        },
        provider,
    )

    first_result = asyncio.run(
        service.send_message(
            first_id,
            InstagramMessageSendRequest(
                first_recipient,
                text="first",
                correlation_id="correlation-a",
            ),
        )
    )
    second_result = asyncio.run(
        service.send_message(
            second_id,
            InstagramMessageSendRequest(
                second_recipient,
                text="second",
                correlation_id="correlation-b",
            ),
        )
    )

    assert first_result.recipient_id == first_recipient
    assert first_result.correlation_id == "correlation-a"
    assert second_result.recipient_id == second_recipient
    assert second_result.correlation_id == "correlation-b"
    assert [call[0] for call in provider.calls] == [first_id, second_id]


def test_send_service_rejects_recipient_without_existing_conversation() -> None:
    connection_id = InstagramConnectionId("connection")
    recipient_id = InstagramUserId("recipient")
    permissions = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_messages",
        }
    )
    provider = FakeInstagramOutboundMessageProvider()
    service = build_service(
        {
            connection_id: InstagramConnection(
                connection_id,
                InstagramAccountId("account"),
                permissions,
                True,
            )
        },
        {(connection_id, recipient_id): False},
        provider,
    )

    with pytest.raises(InstagramMessageRecipientIneligibleError):
        asyncio.run(
            service.send_message(
                connection_id,
                InstagramMessageSendRequest(recipient_id, text="hello"),
            )
        )

    assert provider.calls == []


def test_send_service_validates_payload_before_eligibility_or_provider() -> None:
    connection_id = InstagramConnectionId("connection")
    recipient_id = InstagramUserId("recipient")
    permissions = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_messages",
        }
    )
    provider = FakeInstagramOutboundMessageProvider()
    eligibility = FakeInstagramMessageRecipientEligibilityChecker(
        {(connection_id, recipient_id): True}
    )
    service = InstagramMessageSendService(
        FakeInstagramConnectionReader(
            {
                connection_id: InstagramConnection(
                    connection_id,
                    InstagramAccountId("account"),
                    permissions,
                    True,
                )
            }
        ),
        eligibility,
        provider,
        InstagramMessageSendAccessPolicy(),
        InstagramMessagePayloadPolicy(),
    )

    with pytest.raises(InstagramMessagePayloadInvalidError):
        asyncio.run(
            service.send_message(
                connection_id,
                InstagramMessageSendRequest(recipient_id, text=" "),
            )
        )

    assert eligibility.calls == []
    assert provider.calls == []
