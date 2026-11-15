"""Read-only host integration boundary for authoritative occupied periods."""

from typing import Protocol

from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval


class BusyIntervalReader(Protocol):
    async def list_busy(
        self, tenant_id: str, resource_ids: tuple[str, ...], window: UtcInterval
    ) -> tuple[BusyInterval, ...]: ...
