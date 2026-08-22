"""Tests for timezone-aware datetime validation."""

from datetime import UTC, datetime

import pytest

from integration_auth.domain.validators.datetime_validator import AwareDateTimeValidator


def test_accepts_timezone_aware_datetime() -> None:
    validator = AwareDateTimeValidator()
    value = datetime(2026, 8, 22, 10, 0, tzinfo=UTC)

    assert validator.validate(value, field_name="issued_at") is value


def test_rejects_naive_datetime() -> None:
    validator = AwareDateTimeValidator()
    value = datetime(2026, 8, 22, 10, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        validator.validate(value, field_name="issued_at")
