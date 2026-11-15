"""End-to-end regression against separately specified absolute UTC expectations."""

import pytest

from scheduling.engine import calculate_availability
from tests.support.engine.golden_scenarios import GoldenScenario, golden_scenarios


@pytest.mark.parametrize("scenario", golden_scenarios(), ids=lambda case: case.name)
def test_independent_golden_availability_scenario(scenario: GoldenScenario) -> None:
    actual = calculate_availability(scenario.request)

    assert tuple((slot.resource_id, slot.interval.start) for slot in actual) == scenario.expected
    assert calculate_availability(scenario.request) == actual
