from datetime import UTC, datetime
from uuid import UUID

from business.infrastructure.clock import SystemClock
from business.infrastructure.identifiers import UuidIdentifierGenerator


def test_system_clock_returns_timezone_aware_utc_time() -> None:
    now = SystemClock().now()

    assert now.tzinfo is UTC
    assert abs((datetime.now(UTC) - now).total_seconds()) < 1


def test_uuid_generator_returns_unique_version_four_identifiers() -> None:
    generator = UuidIdentifierGenerator()
    first, second = generator.new_id(), generator.new_id()

    assert isinstance(first, UUID)
    assert first.version == 4
    assert first != second
