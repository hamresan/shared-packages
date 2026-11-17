"""Minimal ASGI request driver for transport integration tests without httpx."""

import json
from collections.abc import Awaitable, Callable
from typing import Any


async def request_asgi(
    app: Callable[..., Awaitable[None]],
    method: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    query_string: bytes = b"",
) -> tuple[int, Any]:
    body = json.dumps(payload).encode() if payload is not None else b""
    response_status = 0
    response_body = bytearray()
    received = False

    async def receive() -> dict[str, object]:
        nonlocal received
        if not received:
            received = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        nonlocal response_status
        if message["type"] == "http.response.start":
            response_status = message["status"]
        elif message["type"] == "http.response.body":
            response_body.extend(message.get("body", b""))

    request_headers = {**(headers or {})}
    if payload is not None:
        request_headers.setdefault("content-type", "application/json")

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string,
        "root_path": "",
        "headers": [(k.lower().encode(), v.encode()) for k, v in request_headers.items()],
        "client": ("test", 1234),
        "server": ("test", 80),
    }
    await app(scope, receive, send)
    return response_status, json.loads(response_body) if response_body else None
