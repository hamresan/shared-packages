"""Maps normalized outbound messages to Meta Send API payloads."""

from collections.abc import Mapping

from instagram_api.domain import InstagramMessageAttachmentType, InstagramMessageSendRequest


class MetaInstagramOutboundPayloadMapper:
    """Builds provider JSON for supported outbound message types."""

    def to_provider(self, request: InstagramMessageSendRequest) -> Mapping[str, object]:
        """Map a validated outbound request to Meta JSON."""

        recipient: Mapping[str, object] = {"id": str(request.recipient_id)}

        if request.text is not None:
            message: Mapping[str, object] = {"text": request.text}
            return {"recipient": recipient, "message": message}

        attachment = request.attachment
        if attachment is None:
            return {"recipient": recipient, "message": {}}

        provider_type = (
            "image"
            if attachment.type is InstagramMessageAttachmentType.IMAGE
            else "video"
        )
        message = {
            "attachment": {
                "type": provider_type,
                "payload": {"url": attachment.url},
            }
        }
        return {"recipient": recipient, "message": message}
