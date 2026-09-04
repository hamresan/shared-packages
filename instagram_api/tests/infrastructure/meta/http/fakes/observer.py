"""Observability fake for Meta HTTP tests."""

from instagram_api.infrastructure.meta.http import MetaHttpObserver


class RecordingMetaHttpObserver(MetaHttpObserver):
    """Records sanitized HTTP lifecycle metadata."""

    def __init__(self) -> None:
        self.started: list[tuple[str, str]] = []
        self.responses: list[tuple[str, str, int]] = []
        self.failures: list[tuple[str, str, str]] = []

    def request_started(self, *, method: str, url: str) -> None:
        self.started.append((method, url))

    def response_received(self, *, method: str, url: str, status_code: int) -> None:
        self.responses.append((method, url, status_code))

    def request_failed(self, *, method: str, url: str, error_type: str) -> None:
        self.failures.append((method, url, error_type))
