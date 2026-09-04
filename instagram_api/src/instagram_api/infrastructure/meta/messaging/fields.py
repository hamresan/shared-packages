"""Field parsing helpers for Meta Instagram messaging payloads."""

from collections.abc import Mapping, Sequence
from typing import cast

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramMessagingFieldParser:
    """Parses common Meta messaging field shapes."""

    def mapping(self, value: object, label: str) -> Mapping[str, object]:
        """Return a typed mapping or raise a normalized provider error."""

        if not isinstance(value, Mapping):
            raise MetaInvalidResponseError(
                message=f"Meta {label} payload is invalid.",
                status_code=200,
            )
        return cast(Mapping[str, object], value)

    def sequence(self, value: object, label: str) -> Sequence[object]:
        """Return a typed sequence or raise a normalized provider error."""

        if not isinstance(value, Sequence) or isinstance(value, str | bytes):
            raise MetaInvalidResponseError(
                message=f"Meta {label} collection is invalid.",
                status_code=200,
            )
        return cast(Sequence[object], value)

    def required_string(self, value: object, label: str) -> str:
        """Return a required string value."""

        if not isinstance(value, str) or not value:
            raise MetaInvalidResponseError(
                message=f"Meta payload is missing a valid {label}.",
                status_code=200,
            )
        return value
