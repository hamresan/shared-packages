"""Trusted tenant-scoped calendar snapshot for availability calculation."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from scheduling.domain.time import IanaTimeZone

from .blocked_period import BlockedPeriod
from .exception import CalendarException
from .holiday import AnnualClosure
from .schedule import WeeklySchedule
from .window import WorkingWindow


class CalendarScope(StrEnum):
    ORGANIZATION = "organization"
    LOCATION = "location"
    RESOURCE = "resource"


@dataclass(frozen=True, slots=True)
class Calendar:
    """An immutable calendar snapshot; authoritative tenant scope comes from the host."""

    calendar_id: str
    tenant_id: str
    scope: CalendarScope
    scope_id: str
    timezone: IanaTimeZone
    weekly_schedule: WeeklySchedule
    exceptions: tuple[CalendarException, ...] = ()
    annual_closures: tuple[AnnualClosure, ...] = ()
    blocked_periods: tuple[BlockedPeriod, ...] = ()
    version: int = 1
    archived: bool = False

    def __post_init__(self) -> None:
        if not self.calendar_id.strip() or not self.tenant_id.strip() or not self.scope_id.strip():
            raise ValueError("Calendar, tenant, and scope identifiers must be non-empty.")
        if self.version < 1:
            raise ValueError("Calendar version must be positive.")
        exception_days = [exception.day for exception in self.exceptions]
        if len(exception_days) != len(set(exception_days)):
            raise ValueError("A calendar may have only one exception per local date.")

    def windows_for(self, day: date) -> tuple[WorkingWindow, ...]:
        """Hard closures override replacement hours at this scope."""
        if self.is_closed(day):
            return ()
        for exception in self.exceptions:
            if exception.day == day:
                if exception.closed:
                    return ()
                if exception.override_windows is not None:
                    return exception.override_windows
        return self.weekly_schedule.windows_for(day)

    def is_closed(self, day: date) -> bool:
        return (
            self.archived
            or any(holiday.matches(day) for holiday in self.annual_closures)
            or any(exception.day == day and exception.closed for exception in self.exceptions)
        )
