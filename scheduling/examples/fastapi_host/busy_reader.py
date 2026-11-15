"""Demo has no reservations; real hosts supply their authoritative booking reader."""

from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval


class DemoBusyIntervalReader:
    async def list_busy(
        self, tenant_id: str, resource_ids: tuple[str, ...], window: UtcInterval
    ) -> tuple[BusyInterval, ...]:
        return ()
