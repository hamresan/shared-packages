"""Typed, bounded inputs and outputs for the pure availability engine."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from scheduling.domain.calendar import Calendar
from scheduling.domain.time import UtcInterval

from .request_validator import validate_availability_request


@dataclass(frozen=True, slots=True)
class BusyInterval:
    resource_id: str
    interval: UtcInterval

    def __post_init__(self) -> None:
        if not self.resource_id.strip():
            raise ValueError("Busy interval resource identifier cannot be empty.")


@dataclass(frozen=True, slots=True)
class AvailableSlot:
    resource_id: str
    interval: UtcInterval


@dataclass(frozen=True, slots=True)
class AvailabilityRequest:
    """A complete snapshot request; no calendar or eligibility lookup occurs here."""

    organization: Calendar
    location: Calendar
    resources: tuple[Calendar, ...]
    query_window: UtcInterval
    duration: timedelta
    step: timedelta
    now: datetime
    busy_intervals: tuple[BusyInterval, ...] = ()
    buffer_before: timedelta = timedelta()
    buffer_after: timedelta = timedelta()
    minimum_notice: timedelta = timedelta()
    maximum_horizon: timedelta = timedelta(days=31)

    def __post_init__(self) -> None:
        validate_availability_request(self)
