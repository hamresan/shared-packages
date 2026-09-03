"""Clock abstraction for deterministic time-dependent behavior."""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Provide the current time through an injected boundary."""

    def now(self) -> datetime:
        """Return the current timezone-aware timestamp."""
        ...
