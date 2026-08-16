from typing import Protocol

import httpx


class JsonHttpClient(Protocol):
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response: ...

    def post(
        self,
        url: str,
        *,
        json: object | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response: ...
