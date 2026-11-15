"""Time-specific errors raised by scheduling domain primitives."""


class InvalidTimeZoneError(ValueError):
    """An IANA time zone identifier cannot be resolved."""


class InvalidIntervalError(ValueError):
    """An interval contains invalid, unordered, or non-UTC instants."""


class AmbiguousLocalTimeError(ValueError):
    """A local time has two possible UTC instants and needs an explicit policy."""


class NonexistentLocalTimeError(ValueError):
    """A local time does not exist because of a timezone transition."""
