"""Tests for UnixTimestampMapper."""

from datetime import UTC, datetime

import pytest

from integration_auth.application.mappers.time import UnixTimestampMapper


def test_maps_unix_timestamp_to_aware_utc_datetime() -> None:
    assert UnixTimestampMapper().to_datetime(1787390042) == datetime(
        2026,
        8,
        22,
        9,
        14,
        2,
        tzinfo=UTC,
    )


def test_rejects_negative_timestamp() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        UnixTimestampMapper().to_datetime(-1)
