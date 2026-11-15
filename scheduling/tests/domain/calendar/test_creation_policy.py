from dataclasses import replace

import pytest

from scheduling.domain.calendar import CalendarScope
from scheduling.domain.calendar.creation_policy import validate_new_calendar
from tests.support.calendar_factory import make_calendar


def test_new_active_calendar_starts_at_version_one() -> None:
    validate_new_calendar(make_calendar(CalendarScope.RESOURCE, "resource-a"))


def test_creation_rejects_noninitial_versions_and_archived_calendars() -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")

    with pytest.raises(ValueError, match="version one"):
        validate_new_calendar(replace(calendar, version=3))
    with pytest.raises(ValueError, match="active"):
        validate_new_calendar(replace(calendar, archived=True))
