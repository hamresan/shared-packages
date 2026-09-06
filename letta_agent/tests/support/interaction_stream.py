from collections.abc import AsyncIterator

from letta_client.types.agents.letta_streaming_response import (
    LettaStreamingResponse,
)


class FakeInteractionStream:
    def __init__(self, events: list[LettaStreamingResponse]) -> None:
        self._events = events

    async def __aiter__(self) -> AsyncIterator[LettaStreamingResponse]:
        for event in self._events:
            yield event
