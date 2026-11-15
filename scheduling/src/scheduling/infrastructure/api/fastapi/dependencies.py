"""Explicit application dependencies provided by a consuming host."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from scheduling.application.models import TrustedActor
from scheduling.application.use_cases import (
    AddBlockedPeriod,
    ArchiveCalendar,
    CreateCalendar,
    FindAvailability,
    GetCalendar,
    ListCalendars,
    RemoveBlockedPeriod,
    RemoveDateException,
    SetDateException,
    UpdateWeeklySchedule,
)

from .availability_mapper import AvailabilityHttpMapper
from .calendar_mapper import CalendarHttpMapper


class Clock(Protocol):
    def now(self) -> datetime: ...


@dataclass(frozen=True, slots=True)
class CalendarHttpDependencies:
    """Adapter composition; application use cases themselves keep narrow contracts."""

    get_actor: Callable[[], Awaitable[TrustedActor]]
    clock: Clock
    calendar_mapper: CalendarHttpMapper
    availability_mapper: AvailabilityHttpMapper
    create: CreateCalendar
    get: GetCalendar
    list_calendars: ListCalendars
    update_schedule: UpdateWeeklySchedule
    set_exception: SetDateException
    remove_exception: RemoveDateException
    add_block: AddBlockedPeriod
    remove_block: RemoveBlockedPeriod
    archive: ArchiveCalendar
    availability: FindAvailability
