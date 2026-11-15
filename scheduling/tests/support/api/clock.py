"""Deterministic UTC clock for HTTP tests."""

from datetime import UTC, datetime


class FixedUtcClock:
    def now(self) -> datetime:
        return datetime(2026, 11, 15, 0, tzinfo=UTC)
