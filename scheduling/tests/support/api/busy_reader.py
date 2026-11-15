"""Observable external occupied-interval reader."""

from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval


class FakeBusyIntervalReader:
    def __init__(self, intervals: tuple[BusyInterval, ...] = ()) -> None:
        self.intervals = intervals
        self.calls: list[tuple[str, tuple[str, ...], UtcInterval]] = []

    async def list_busy(
        self, tenant_id: str, resource_ids: tuple[str, ...], window: UtcInterval
    ) -> tuple[BusyInterval, ...]:
        self.calls.append((tenant_id, resource_ids, window))
        return tuple(item for item in self.intervals if item.resource_id in resource_ids)
