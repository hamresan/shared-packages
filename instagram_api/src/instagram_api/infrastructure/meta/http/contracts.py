"""Contracts for shared Meta HTTP infrastructure."""

from collections.abc import Mapping
from typing import Protocol

from instagram_api.domain import InstagramConnectionId

from .models import MetaHttpMethod, MetaHttpRequest, MetaHttpResponse


class MetaHttpTransport(Protocol):
    """Executes provider requests without exposing a concrete HTTP client."""

    async def send(self, request: MetaHttpRequest) -> MetaHttpResponse:
        """Execute a provider request."""
        ...


class MetaJsonExecutor(Protocol):
    """Executes connection-aware Meta requests returning normalized JSON."""

    async def execute_json(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: MetaHttpMethod,
        path: str,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> Mapping[str, object]:
        """Execute one Meta JSON request for an explicit connection."""
        ...


class MetaHttpObserver(Protocol):
    """Receives structured provider HTTP lifecycle metadata without secrets."""

    def request_started(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
    ) -> None:
        """Record a request-start event."""
        ...

    def response_received(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
        status_code: int,
    ) -> None:
        """Record a response event."""
        ...

    def request_failed(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
        error_type: str,
    ) -> None:
        """Record a request-failure event."""
        ...
