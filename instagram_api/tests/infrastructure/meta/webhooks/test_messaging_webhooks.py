"""Stage 10 Meta messaging webhook normalization tests."""

from instagram_api.domain import (
    InstagramInboundMessageAttachment,
    InstagramMessageEdited,
    InstagramMessageId,
    InstagramMessagePostbackReceived,
    InstagramMessageReaction,
    InstagramMessageReactionAction,
    InstagramMessageRead,
    InstagramMessageReceived,
    InstagramMessagingReferralReceived,
    InstagramUserId,
)
from tests.infrastructure.meta.webhooks.factories import build_meta_webhook_parser


def test_parser_normalizes_inbound_message_with_story_and_attachment_metadata() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,"messaging":['
        b'{"sender":{"id":"sender"},"recipient":{"id":"account"},'
        b'"timestamp":1788523200123,"message":{"mid":"message-1","text":"hello",'
        b'"is_echo":false,"is_self":false,"is_deleted":false,"is_unsupported":false,'
        b'"attachments":[{"type":"image","payload":{"url":"https://example.com/a.jpg"}}],'
        b'"reply_to":{"story":{"id":"story-1","url":"https://example.com/story"}}}}]}]}'
    )

    event = build_meta_webhook_parser().parse(payload)[0]

    assert event.provider_account_id == "account"
    assert isinstance(event.payload, InstagramMessageReceived)
    message = event.payload
    assert message.sender_id == InstagramUserId("sender")
    assert message.recipient_id == InstagramUserId("account")
    assert message.message_id == InstagramMessageId("message-1")
    assert message.text == "hello"
    assert message.attachments == (
        InstagramInboundMessageAttachment(
            attachment_type="image",
            url="https://example.com/a.jpg",
        ),
    )
    assert message.reply_to_story_id == "story-1"
    assert message.reply_to_story_url == "https://example.com/story"


def test_parser_normalizes_postback_read_reaction_edit_and_referral() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,"messaging":['
        b'{"sender":{"id":"user"},"recipient":{"id":"account"},"timestamp":1788523200001,'
        b'"postback":{"mid":"postback-mid","title":"Start","payload":"START"}},'
        b'{"sender":{"id":"user"},"recipient":{"id":"account"},"timestamp":1788523200002,'
        b'"read":{"mid":"read-mid"}},'
        b'{"sender":{"id":"user"},"recipient":{"id":"account"},"timestamp":1788523200003,'
        b'"reaction":{"mid":"reaction-mid","action":"react","reaction":"love","emoji":"❤"}},'
        b'{"sender":{"id":"user"},"recipient":{"id":"account"},"timestamp":1788523200004,'
        b'"message_edit":{"mid":"edit-mid","text":"edited","num_edit":2}},'
        b'{"sender":{"id":"user"},"recipient":{"id":"account"},"timestamp":1788523200005,'
        b'"referral":{"ref":"campaign","source":"ADS","type":"OPEN_THREAD"}}]}]}'
    )

    events = build_meta_webhook_parser().parse(payload)

    assert isinstance(events[0].payload, InstagramMessagePostbackReceived)
    assert events[0].payload.message_id == InstagramMessageId("postback-mid")
    assert events[0].payload.payload == "START"

    assert isinstance(events[1].payload, InstagramMessageRead)
    assert events[1].payload.message_id == InstagramMessageId("read-mid")

    assert isinstance(events[2].payload, InstagramMessageReaction)
    assert events[2].payload.action is InstagramMessageReactionAction.REACT
    assert events[2].payload.emoji == "❤"

    assert isinstance(events[3].payload, InstagramMessageEdited)
    assert events[3].payload.text == "edited"
    assert events[3].payload.edit_count == 2

    assert isinstance(events[4].payload, InstagramMessagingReferralReceived)
    assert events[4].payload.referral_ref == "campaign"
    assert events[4].payload.source == "ADS"


def test_parser_preserves_provider_message_id_and_stable_delivery_event_id() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,"messaging":['
        b'{"sender":{"id":"sender"},"recipient":{"id":"account"},'
        b'"timestamp":1788523200123,"message":{"mid":"provider-message-id","text":"hello"}}]}]}'
    )
    parser = build_meta_webhook_parser()

    first = parser.parse(payload)[0]
    second = parser.parse(payload)[0]

    assert isinstance(first.payload, InstagramMessageReceived)
    assert first.payload.message_id == InstagramMessageId("provider-message-id")
    assert first.event_id == second.event_id


def test_parser_keeps_unknown_messaging_variant_as_generic_event() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,"messaging":['
        b'{"sender":{"id":"sender"},"recipient":{"id":"account"},'
        b'"timestamp":1788523200123,"unknown_event":{"value":"x"}}]}]}'
    )

    event = build_meta_webhook_parser().parse(payload)[0]

    assert event.event_type == "messaging"
    assert event.payload is None
