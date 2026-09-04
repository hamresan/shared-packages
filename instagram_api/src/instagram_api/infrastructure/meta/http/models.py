"""Shared HTTP models for Meta provider infrastructure."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import cast


def empty_string_mapping() -> Mapping[str, str]:
    """Return an explicitly typed empty string mapping."""

    return cast(Mapping[str, str], {})


class MetaHttpMethod(StrEnum):
    """HTTP methods used by Meta provider requests."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


@dataclass(frozen=True, slots=True)
class MetaHttpRequest:
    """Provider request independent of a concrete HTTP client."""

    method: MetaHttpMethod
    url: str
    headers: Mapping[str, str] = field(default_factory=empty_string_mapping)
    params: Mapping[str, str] = field(default_factory=empty_string_mapping)
    json_body: Mapping[str, object] | None = None


@dataclass(frozen=True, slots=True)
class MetaHttpResponse:
    """Provider response independent of a concrete HTTP client."""

    status_code: int
    headers: Mapping[str, str]
    body: bytes
