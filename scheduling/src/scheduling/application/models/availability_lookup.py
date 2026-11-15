"""Tenant-neutral scope and timing inputs for advisory availability lookup."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from scheduling.domain.time import UtcInterval


@dataclass(frozen=True, slots=True)
class AvailabilityLookup:
    organization_id: str
    location_id: str
    resource_ids: tuple[str, ...]
    window: UtcInterval
    duration: timedelta
    step: timedelta
    now: datetime
    buffer_before: timedelta = timedelta()
    buffer_after: timedelta = timedelta()
    minimum_notice: timedelta = timedelta()
    maximum_horizon: timedelta = timedelta(days=31)
