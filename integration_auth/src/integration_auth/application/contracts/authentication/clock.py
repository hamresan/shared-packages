"""Clock contract for application authentication."""

from typing import Protocol


class Clock(Protocol):
    """Provide the current Unix timestamp."""

    def now_timestamp(self) -> int: ...
