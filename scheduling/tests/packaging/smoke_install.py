"""Verify public imports from an installed wheel without development dependencies."""

from scheduling.domain.calendar import Calendar, WorkingWindow
from scheduling.domain.time import IanaTimeZone
from scheduling.engine import AvailabilityRequest, calculate_availability

assert IanaTimeZone("Asia/Muscat").key == "Asia/Muscat"
assert Calendar.__name__ == "Calendar"
assert WorkingWindow.__name__ == "WorkingWindow"
assert AvailabilityRequest.__name__ == "AvailabilityRequest"
assert callable(calculate_availability)
