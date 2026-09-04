"""Transport fake for Meta HTTP tests."""

from collections import deque

from instagram_api.infrastructure.meta.http import (
    MetaHttpRequest,
    MetaHttpResponse,
    MetaHttpTransport,
)


class SequenceMetaHttpTransport(MetaHttpTransport):
    """Returns or raises configured outcomes in sequence."""

    def __init__(self, outcomes: list[MetaHttpResponse | Exception]) -> None:
        self._outcomes = deque(outcomes)
        self.requests: list[MetaHttpRequest] = []

    async def send(self, request: MetaHttpRequest) -> MetaHttpResponse:
        self.requests.append(request)
        outcome = self._outcomes.popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome
