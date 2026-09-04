"""Timestamp parsing for Meta Instagram media."""

from datetime import datetime

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramMediaTimestampParser:
    """Parses provider timestamps into timezone-aware datetime values."""

    def parse(self, value: str) -> datetime:
        """Parse an ISO-8601 timestamp or raise a normalized provider error."""

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MetaInvalidResponseError(
                message="Meta media response contains an invalid timestamp.",
                status_code=200,
            ) from exc
