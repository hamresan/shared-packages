from typing import Protocol

import httpx


class JsonPostClient(Protocol):
    def post(self, url: str, *, json: object | None = None) -> httpx.Response: ...
