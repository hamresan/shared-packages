"""Observability fake for Meta HTTP tests."""

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.http import MetaHttpObserver


class RecordingMetaHttpObserver(MetaHttpObserver):
    """Records sanitized connection-aware HTTP lifecycle metadata."""

    def __init__(self) -> None:
        self.started: list[tuple[InstagramConnectionId, str, str]] = []
        self.responses: list[tuple[InstagramConnectionId, str, str, int]] = []
        self.failures: list[tuple[InstagramConnectionId, str, str, str]] = []

    def request_started(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
    ) -> None:
        self.started.append((connection_id, method, url))

    def response_received(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
        status_code: int,
    ) -> None:
        self.responses.append((connection_id, method, url, status_code))

    def request_failed(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
        error_type: str,
    ) -> None:
        self.failures.append((connection_id, method, url, error_type))
