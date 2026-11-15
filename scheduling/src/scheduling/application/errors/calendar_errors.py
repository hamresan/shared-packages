"""Application-facing failures with no persistence or HTTP coupling."""


class CalendarAlreadyExistsError(ValueError):
    """A calendar already exists for the requested tenant and scope."""


class CalendarNotFoundError(LookupError):
    """A calendar is absent or inaccessible in the trusted tenant."""


class CalendarVersionConflictError(RuntimeError):
    """The calendar changed since the caller's expected version."""


class CrossTenantCalendarError(PermissionError):
    """A mutation attempts to cross a trusted tenant boundary."""
