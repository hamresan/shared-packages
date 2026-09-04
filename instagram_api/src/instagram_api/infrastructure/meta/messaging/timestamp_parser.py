"""Timestamp parsing for Meta Instagram messaging."""

from datetime import datetime

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramMessagingTimestampParser:
    """Parses provider timestamps into datetime values."""

    def parse(self, value: str) -> datetime:
        """Parse an ISO-8601 timestamp."""

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MetaInvalidResponseError(
                message="Meta messaging payload contains an invalid timestamp.",
                status_code=200,
            ) from exc
