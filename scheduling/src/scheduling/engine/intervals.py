"""Pure interval-set operations on half-open UTC ranges."""

from collections.abc import Iterable

from scheduling.domain.time import UtcInterval


def merge_intervals(intervals: Iterable[UtcInterval]) -> tuple[UtcInterval, ...]:
    ordered = sorted(intervals, key=lambda interval: (interval.start, interval.end))
    if not ordered:
        return ()

    merged = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.start <= previous.end:
            merged[-1] = UtcInterval(previous.start, max(previous.end, current.end))
        else:
            merged.append(current)
    return tuple(merged)


def intersect_intervals(
    left: Iterable[UtcInterval], right: Iterable[UtcInterval]
) -> tuple[UtcInterval, ...]:
    result: list[UtcInterval] = []
    left_ordered = merge_intervals(left)
    right_ordered = merge_intervals(right)
    left_index = right_index = 0
    while left_index < len(left_ordered) and right_index < len(right_ordered):
        first = left_ordered[left_index]
        second = right_ordered[right_index]
        start = max(first.start, second.start)
        end = min(first.end, second.end)
        if start < end:
            result.append(UtcInterval(start, end))
        if first.end <= second.end:
            left_index += 1
        else:
            right_index += 1
    return tuple(result)


def subtract_intervals(
    allowed: Iterable[UtcInterval], forbidden: Iterable[UtcInterval]
) -> tuple[UtcInterval, ...]:
    remaining: list[UtcInterval] = []
    blocked = merge_intervals(forbidden)
    for interval in merge_intervals(allowed):
        cursor = interval.start
        for exclusion in blocked:
            if exclusion.end <= cursor:
                continue
            if exclusion.start >= interval.end:
                break
            if exclusion.start > cursor:
                remaining.append(UtcInterval(cursor, exclusion.start))
            cursor = min(interval.end, max(cursor, exclusion.end))
            if cursor >= interval.end:
                break
        if cursor < interval.end:
            remaining.append(UtcInterval(cursor, interval.end))
    return tuple(remaining)
