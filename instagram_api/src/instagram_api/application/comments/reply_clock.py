"""Clock boundary for time-sensitive private reply eligibility."""

from datetime import datetime
from typing import Protocol


class InstagramReplyClock(Protocol):
    """Supplies current time for private-reply eligibility decisions."""

    def now(self) -> datetime:
        """Return the current timezone-aware datetime."""
        ...
