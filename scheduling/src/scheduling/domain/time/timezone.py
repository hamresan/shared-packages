"""Validated IANA time zone identity."""

from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .errors import InvalidTimeZoneError


@dataclass(frozen=True, slots=True)
class IanaTimeZone:
    """Preserve the zone identifier rather than a season-dependent UTC offset."""

    key: str

    def __post_init__(self) -> None:
        if not self.key or self.key != self.key.strip():
            raise InvalidTimeZoneError("A non-empty IANA timezone name is required.")
        self.to_zoneinfo()

    def to_zoneinfo(self) -> ZoneInfo:
        try:
            return ZoneInfo(self.key)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise InvalidTimeZoneError(f"Unknown IANA timezone: {self.key!r}.") from exc
