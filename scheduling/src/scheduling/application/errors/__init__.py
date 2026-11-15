"""Public calendar-management failure categories."""

from .calendar_errors import (
    CalendarAlreadyExistsError,
    CalendarNotFoundError,
    CalendarVersionConflictError,
    CrossTenantCalendarError,
)

__all__ = [
    "CalendarAlreadyExistsError",
    "CalendarNotFoundError",
    "CalendarVersionConflictError",
    "CrossTenantCalendarError",
]
