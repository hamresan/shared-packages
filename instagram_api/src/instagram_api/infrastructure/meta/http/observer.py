"""Default observability implementations for Meta HTTP calls."""

from .contracts import MetaHttpObserver


class NullMetaHttpObserver(MetaHttpObserver):
    """Observer implementation that intentionally performs no logging."""

    def request_started(self, *, method: str, url: str) -> None:
        del method, url

    def response_received(self, *, method: str, url: str, status_code: int) -> None:
        del method, url, status_code

    def request_failed(self, *, method: str, url: str, error_type: str) -> None:
        del method, url, error_type
