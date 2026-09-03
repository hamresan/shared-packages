"""Meta HTTP transport contract."""

from collections.abc import Mapping
from typing import Protocol

from .models import MetaHttpResponse


class MetaHttpTransport(Protocol):
    """Transport abstraction implemented by provider HTTP adapters."""

    async def post_form(self, *, url: str, data: Mapping[str, str]) -> MetaHttpResponse:
        """POST form data and return a normalized response."""
        ...

    async def get(self, *, url: str, params: Mapping[str, str]) -> MetaHttpResponse:
        """GET a provider resource and return a normalized response."""
        ...
