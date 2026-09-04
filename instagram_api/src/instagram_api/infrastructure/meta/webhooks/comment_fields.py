"""Field parsing helpers for Meta comment webhook payloads."""

from collections.abc import Mapping
from typing import cast


class MetaInstagramCommentWebhookFieldParser:
    """Parses optional nested comment webhook fields."""

    def mapping(self, value: object) -> Mapping[str, object] | None:
        """Return a typed mapping when present."""

        if not isinstance(value, Mapping):
            return None
        return cast(Mapping[str, object], value)

    def optional_string(self, value: object) -> str | None:
        """Return an optional non-empty string."""

        return value if isinstance(value, str) and value else None

    def nested_id(self, value: object) -> str | None:
        """Return an optional nested object ID."""

        mapping = self.mapping(value)
        if mapping is None:
            return None
        return self.optional_string(mapping.get("id"))
