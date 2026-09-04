"""Typed field parsing for Meta Instagram webhook payloads."""

from collections.abc import Mapping, Sequence
from typing import cast

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramWebhookFieldParser:
    """Parses common Meta webhook collection and mapping shapes."""

    def mapping(self, value: object, label: str) -> Mapping[str, object]:
        """Return a typed mapping."""

        if not isinstance(value, Mapping):
            raise MetaInvalidResponseError(
                message=f"Meta webhook {label} is invalid.",
                status_code=200,
            )
        return cast(Mapping[str, object], value)

    def sequence(self, value: object, label: str) -> Sequence[object]:
        """Return a typed sequence."""

        if not isinstance(value, Sequence) or isinstance(value, str | bytes):
            raise MetaInvalidResponseError(
                message=f"Meta webhook {label} collection is invalid.",
                status_code=200,
            )
        return cast(Sequence[object], value)

    def required_string(self, value: object, label: str) -> str:
        """Return a required non-empty string."""

        if not isinstance(value, str) or not value:
            raise MetaInvalidResponseError(
                message=f"Meta webhook is missing a valid {label}.",
                status_code=200,
            )
        return value

    def optional_int(self, value: object) -> int | None:
        """Return an integer when Meta supplies one."""

        return value if isinstance(value, int) and not isinstance(value, bool) else None
