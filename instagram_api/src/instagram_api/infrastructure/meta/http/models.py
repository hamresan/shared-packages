"""Shared HTTP models for Meta provider infrastructure."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


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
    headers: Mapping[str, str] = field(default_factory=dict)
    params: Mapping[str, str] = field(default_factory=dict)
    json_body: Mapping[str, object] | None = None


@dataclass(frozen=True, slots=True)
class MetaHttpResponse:
    """Provider response independent of a concrete HTTP client."""

    status_code: int
    headers: Mapping[str, str]
    body: bytes
