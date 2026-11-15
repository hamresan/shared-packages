"""Deterministic per-resource candidate availability calculation."""

from scheduling.domain.time import UtcInterval

from .calendar_expander import expand_calendar
from .intervals import intersect_intervals
from .models import AvailabilityRequest, AvailableSlot
from .occupancy import occupied_window


def calculate_availability(request: AvailabilityRequest) -> tuple[AvailableSlot, ...]:
    """Calculate advisory slots; final reservation is strictly host-owned."""
    expansion_window = UtcInterval(
        request.query_window.start - request.buffer_before,
        request.query_window.end + request.buffer_after,
    )
    parent_hours = intersect_intervals(
        expand_calendar(request.organization, expansion_window),
        expand_calendar(request.location, expansion_window),
    )
    parent_blocked = (
        *(block.interval for block in request.organization.blocked_periods),
        *(block.interval for block in request.location.blocked_periods),
    )
    earliest_slot = max(request.query_window.start, request.now + request.minimum_notice)
    latest_slot_end = min(request.query_window.end, request.now + request.maximum_horizon)
    results: list[AvailableSlot] = []

    for resource in request.resources:
        working_intervals = intersect_intervals(
            parent_hours, expand_calendar(resource, expansion_window)
        )
        excluded = (
            *parent_blocked,
            *(block.interval for block in resource.blocked_periods),
            *(
                busy.interval
                for busy in request.busy_intervals
                if busy.resource_id == resource.scope_id
            ),
        )
        for allowed in working_intervals:
            cursor = allowed.start + request.buffer_before
            while cursor + request.duration + request.buffer_after <= allowed.end:
                end = cursor + request.duration
                if cursor >= earliest_slot and end <= latest_slot_end:
                    slot = UtcInterval(cursor, end)
                    occupied = occupied_window(slot, request.buffer_before, request.buffer_after)
                    if not any(occupied.overlaps(busy) for busy in excluded):
                        results.append(AvailableSlot(resource.scope_id, slot))
                cursor += request.step

    return tuple(sorted(results, key=lambda slot: (slot.interval.start, slot.resource_id)))
