"""New managed calendars must begin as active first revisions."""

from .calendar import Calendar


def validate_new_calendar(calendar: Calendar) -> None:
    if calendar.version != 1 or calendar.archived:
        raise ValueError("A newly created calendar must be active at version one.")
