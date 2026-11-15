"""An explicit local-date closure or complete schedule replacement."""

from dataclasses import dataclass
from datetime import date

from .schedule_validator import validate_daily_windows
from .window import WorkingWindow


@dataclass(frozen=True, slots=True)
class CalendarException:
    day: date
    closed: bool = False
    override_windows: tuple[WorkingWindow, ...] | None = None

    def __post_init__(self) -> None:
        if self.closed and self.override_windows is not None:
            raise ValueError("A closed date cannot also define replacement hours.")
        if self.override_windows is not None:
            validate_daily_windows(self.override_windows)
