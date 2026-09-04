"""Timestamp parsing for Meta Instagram comments."""

from datetime import datetime

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramCommentTimestampParser:
    """Parses provider comment timestamps."""

    def parse(self, value: str) -> datetime:
        """Parse an ISO-8601 timestamp."""

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MetaInvalidResponseError(
                message="Meta comment response contains an invalid timestamp.",
                status_code=200,
            ) from exc
