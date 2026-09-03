"""Provider HTTP response model."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaHttpResponse:
    """Small transport-neutral HTTP response."""

    status_code: int
    payload: dict[str, object]
