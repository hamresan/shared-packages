import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


class ConcurrentRunner:
    async def run(
        self,
        operations: Sequence[Callable[[], Awaitable[T]]],
    ) -> list[T | BaseException]:
        start_event = asyncio.Event()

        async def run_after_release(operation: Callable[[], Awaitable[T]]) -> T:
            await start_event.wait()
            return await operation()

        tasks = [asyncio.create_task(run_after_release(operation)) for operation in operations]
        start_event.set()
        return list(await asyncio.gather(*tasks, return_exceptions=True))
