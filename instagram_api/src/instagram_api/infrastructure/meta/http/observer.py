"""Default observability implementations for Meta HTTP calls."""

from instagram_api.domain import InstagramConnectionId

from .contracts import MetaHttpObserver


class NullMetaHttpObserver(MetaHttpObserver):
    """Observer implementation that intentionally performs no logging."""

    def request_started(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
    ) -> None:
        del connection_id, method, url

    def response_received(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
        status_code: int,
    ) -> None:
        del connection_id, method, url, status_code

    def request_failed(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: str,
        url: str,
        error_type: str,
    ) -> None:
        del connection_id, method, url, error_type
