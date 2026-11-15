"""Verify public imports from an installed wheel without development dependencies."""

from scheduling.application.models import TrustedActor
from scheduling.application.use_cases import CreateCalendar
from scheduling.domain.calendar import Calendar, WorkingWindow
from scheduling.domain.time import IanaTimeZone
from scheduling.engine import AvailabilityRequest, calculate_availability

assert IanaTimeZone("Asia/Muscat").key == "Asia/Muscat"
assert Calendar.__name__ == "Calendar"
assert WorkingWindow.__name__ == "WorkingWindow"
assert AvailabilityRequest.__name__ == "AvailabilityRequest"
assert callable(calculate_availability)
assert CreateCalendar.__name__ == "CreateCalendar"
assert TrustedActor("tenant-a", "actor-a").tenant_id == "tenant-a"
