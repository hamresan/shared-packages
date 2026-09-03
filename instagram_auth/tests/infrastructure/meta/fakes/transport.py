"""Deterministic Meta HTTP transport fake."""

from collections.abc import Mapping

from instagram_auth.infrastructure.meta.http import MetaHttpResponse, MetaHttpTransport


class FakeMetaHttpTransport(MetaHttpTransport):
    """Queue responses or exceptions and capture provider requests."""

    def __init__(self) -> None:
        self.post_results: list[MetaHttpResponse | Exception] = []
        self.get_results: list[MetaHttpResponse | Exception] = []
        self.post_calls: list[tuple[str, dict[str, str]]] = []
        self.get_calls: list[tuple[str, dict[str, str]]] = []

    async def post_form(self, *, url: str, data: Mapping[str, str]) -> MetaHttpResponse:
        self.post_calls.append((url, dict(data)))
        result = self.post_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    async def get(self, *, url: str, params: Mapping[str, str]) -> MetaHttpResponse:
        self.get_calls.append((url, dict(params)))
        result = self.get_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result
