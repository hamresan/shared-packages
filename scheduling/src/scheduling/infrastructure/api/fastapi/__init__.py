"""Public optional HTTP adapter composition API."""

from .availability_mapper import AvailabilityHttpMapper
from .calendar_mapper import CalendarHttpMapper
from .dependencies import CalendarHttpDependencies, Clock
from .error_handlers import install_calendar_error_handlers
from .router import create_calendar_router

__all__ = [
    "AvailabilityHttpMapper",
    "CalendarHttpDependencies",
    "CalendarHttpMapper",
    "Clock",
    "create_calendar_router",
    "install_calendar_error_handlers",
]
