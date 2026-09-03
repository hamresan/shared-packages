"""Test fakes for application contracts."""

from .clock import FixedClock
from .state_generator import FixedStateGenerator

__all__ = ["FixedClock", "FixedStateGenerator"]
