"""Full resource occupancy interval including preparation and cleanup buffers."""

from datetime import timedelta

from scheduling.domain.time import UtcInterval


def occupied_window(slot: UtcInterval, before: timedelta, after: timedelta) -> UtcInterval:
    return UtcInterval(slot.start - before, slot.end + after)
