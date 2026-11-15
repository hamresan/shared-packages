"""Explicitly resolve local wall times across DST transitions."""

from datetime import UTC, date, datetime, time
from typing import Literal

from .errors import AmbiguousLocalTimeError, NonexistentLocalTimeError
from .timezone import IanaTimeZone

AmbiguousTimePolicy = Literal["reject", "earlier", "later"]


def resolve_local_datetime(
    day: date,
    local_time: time,
    zone: IanaTimeZone,
    *,
    ambiguous: AmbiguousTimePolicy = "reject",
) -> datetime:
    """Resolve a wall time without silently choosing either occurrence at DST overlap.

    ``earlier`` and ``later`` refer to chronological UTC instants, not fold numbers.
    Nonexistent times are always rejected at this primitive's boundary.
    """
    if isinstance(day, datetime):
        raise TypeError("day must be a date without a time component.")
    if local_time.tzinfo is not None:
        raise TypeError("local_time must be a timezone-naive time.")
    if ambiguous not in ("reject", "earlier", "later"):
        raise ValueError("ambiguous must be reject, earlier, or later.")

    zoneinfo = zone.to_zoneinfo()
    naive = datetime.combine(day, local_time)
    candidates: dict[datetime, datetime] = {}

    for fold in (0, 1):
        candidate = naive.replace(tzinfo=zoneinfo, fold=fold)
        round_trip = candidate.astimezone(UTC).astimezone(zoneinfo)
        candidate_utc = candidate.astimezone(UTC)
        if round_trip.replace(tzinfo=None) == naive:
            candidates[candidate_utc] = candidate

    if not candidates:
        raise NonexistentLocalTimeError(f"{naive.isoformat()} does not exist in {zone.key}.")

    ordered = [candidates[instant] for instant in sorted(candidates)]
    if len(ordered) > 1:
        if ambiguous == "reject":
            raise AmbiguousLocalTimeError(
                f"{naive.isoformat()} is ambiguous in {zone.key}; choose a policy."
            )
        return ordered[0] if ambiguous == "earlier" else ordered[-1]

    return ordered[0]
