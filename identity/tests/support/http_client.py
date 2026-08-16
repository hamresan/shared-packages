from typing import Protocol

import httpx


class JsonGetClient(Protocol):
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response: ...
