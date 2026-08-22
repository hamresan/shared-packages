"""FastAPI request builder for presentation unit tests."""

from collections.abc import Mapping

from fastapi import Request
from starlette.types import Message, Receive, Scope


class FastApiRequestBuilder:
    """Build an isolated HTTP request with deterministic ASGI scope data."""

    def build(
        self,
        *,
        method: str = "GET",
        path: str = "/protected",
        raw_path: bytes | None = None,
        query_string: bytes = b"",
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
    ) -> Request:
        encoded_headers: list[tuple[bytes, bytes]] = []
        for name, value in (headers or {}).items():
            encoded_headers.append((name.lower().encode("latin-1"), value.encode("latin-1")))

        scope: Scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "scheme": "http",
            "method": method,
            "root_path": "",
            "path": path,
            "raw_path": raw_path if raw_path is not None else path.encode("ascii"),
            "query_string": query_string,
            "headers": encoded_headers,
        }

        async def receive() -> Message:
            return {"type": "http.request", "body": body, "more_body": False}

        receive_callable: Receive = receive
        return Request(scope, receive_callable)
