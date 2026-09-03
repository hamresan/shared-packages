"""OAuth state generation boundary."""

from typing import Protocol


class StateGenerator(Protocol):
    """Generate opaque OAuth state values through an injected implementation."""

    def generate(self) -> str:
        """Return a newly generated opaque state value."""
        ...
