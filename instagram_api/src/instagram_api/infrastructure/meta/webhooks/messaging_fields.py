"""Field parsing helpers for Meta messaging webhook items."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import cast

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramMessagingWebhookFieldParser:
    """Parses typed fields from Meta messaging webhook payloads."""

    def mapping(self, value: object, label: str) -> Mapping[str, object]:
        """Return a typed mapping."""

        if not isinstance(value, Mapping):
            raise MetaInvalidResponseError(
                message=f"Meta messaging webhook {label} is invalid.",
                status_code=200,
            )
        return cast(Mapping[str, object], value)

    def required_id(self, value: object, label: str) -> str:
        """Return a required nested ID."""

        mapping = self.mapping(value, label)
        identifier = mapping.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise MetaInvalidResponseError(
                message=f"Meta messaging webhook is missing a valid {label} id.",
                status_code=200,
            )
        return identifier

    def timestamp(self, value: object) -> datetime:
        """Parse Meta's messaging timestamp, which is expressed in milliseconds."""

        if not isinstance(value, int) or isinstance(value, bool):
            raise MetaInvalidResponseError(
                message="Meta messaging webhook timestamp is invalid.",
                status_code=200,
            )
        return datetime.fromtimestamp(value / 1000, tz=UTC)

    def optional_string(self, value: object) -> str | None:
        """Return an optional string."""

        return value if isinstance(value, str) else None

    def optional_int(self, value: object) -> int | None:
        """Return an optional integer."""

        return value if isinstance(value, int) and not isinstance(value, bool) else None

    def optional_bool(self, value: object) -> bool:
        """Return a boolean when present, otherwise False."""

        return value if isinstance(value, bool) else False

    def sequence(self, value: object) -> Sequence[object]:
        """Return an optional sequence."""

        if value is None:
            return ()
        if not isinstance(value, Sequence) or isinstance(value, str | bytes):
            raise MetaInvalidResponseError(
                message="Meta messaging webhook attachment collection is invalid.",
                status_code=200,
            )
        return cast(Sequence[object], value)
