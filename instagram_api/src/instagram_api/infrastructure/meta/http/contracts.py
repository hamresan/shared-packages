"""Contracts for shared Meta HTTP infrastructure."""

from typing import Protocol

from .models import MetaHttpRequest, MetaHttpResponse


class MetaHttpTransport(Protocol):
    """Executes provider requests without exposing a concrete HTTP client."""

    async def send(self, request: MetaHttpRequest) -> MetaHttpResponse:
        """Execute a provider request."""
        ...


class MetaHttpObserver(Protocol):
    """Receives structured provider HTTP lifecycle metadata without secrets."""

    def request_started(self, *, method: str, url: str) -> None:
        """Record a request-start event."""
        ...

    def response_received(self, *, method: str, url: str, status_code: int) -> None:
        """Record a response event."""
        ...

    def request_failed(self, *, method: str, url: str, error_type: str) -> None:
        """Record a request-failure event."""
        ...
