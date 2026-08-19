from datetime import UTC, datetime

import pytest

from subscription import TimezoneAwareDatetimeValidator


def test_timezone_aware_datetime_validator_accepts_aware_datetime() -> None:
    TimezoneAwareDatetimeValidator().validate(datetime(2026, 8, 19, tzinfo=UTC), "at")


def test_timezone_aware_datetime_validator_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        TimezoneAwareDatetimeValidator().validate(datetime(2026, 8, 19), "at")


def test_timezone_aware_datetime_validator_accepts_none_for_optional_value() -> None:
    TimezoneAwareDatetimeValidator().validate_optional(None, "at")
