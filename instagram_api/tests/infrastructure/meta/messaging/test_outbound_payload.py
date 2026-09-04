"""Meta outbound message payload mapping tests."""

from instagram_api.domain import (
    InstagramMessageAttachment,
    InstagramMessageAttachmentType,
    InstagramMessageSendRequest,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.messaging import MetaInstagramOutboundPayloadMapper


def test_payload_mapper_maps_text_without_correlation_metadata() -> None:
    payload = MetaInstagramOutboundPayloadMapper().to_provider(
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            text="hello",
            correlation_id="host-correlation",
        )
    )

    assert payload == {
        "recipient": {"id": "recipient"},
        "message": {"text": "hello"},
    }


def test_payload_mapper_maps_supported_image_and_video_attachments() -> None:
    mapper = MetaInstagramOutboundPayloadMapper()

    image = mapper.to_provider(
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            attachment=InstagramMessageAttachment(
                InstagramMessageAttachmentType.IMAGE,
                "https://example.com/image.jpg",
            ),
        )
    )
    video = mapper.to_provider(
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            attachment=InstagramMessageAttachment(
                InstagramMessageAttachmentType.VIDEO,
                "https://example.com/video.mp4",
            ),
        )
    )

    assert image["message"] == {
        "attachment": {
            "type": "image",
            "payload": {"url": "https://example.com/image.jpg"},
        }
    }
    assert video["message"] == {
        "attachment": {
            "type": "video",
            "payload": {"url": "https://example.com/video.mp4"},
        }
    }
