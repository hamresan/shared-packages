"""Parses Meta Send API responses."""

from collections.abc import Mapping

from instagram_api.domain import InstagramMessageId, InstagramUserId
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramMessageSendResponseParser:
    """Parses successful Send API responses."""

    def message_id(self, payload: Mapping[str, object]) -> InstagramMessageId:
        """Return the provider message ID."""

        value = payload.get("message_id")
        if not isinstance(value, str) or not value:
            raise MetaInvalidResponseError(
                message="Meta send response is missing a valid message_id.",
                status_code=200,
            )
        return InstagramMessageId(value)

    def recipient_id(self, payload: Mapping[str, object]) -> InstagramUserId | None:
        """Return the provider-confirmed recipient ID when supplied."""

        value = payload.get("recipient_id")
        if isinstance(value, str) and value:
            return InstagramUserId(value)
        return None
