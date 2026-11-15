"""Benchmark fixtures validate their own deterministic results and public limits."""

from datetime import timedelta

import pytest

from benchmarks.availability_benchmark import measure
from benchmarks.availability_scenario import BenchmarkSize, make_benchmark_request


def test_benchmark_scenario_uses_distinct_resource_shifts_and_busy_intervals() -> None:
    request = make_benchmark_request(BenchmarkSize(resources=2, days=7))

    assert request.resources[0].weekly_schedule != request.resources[1].weekly_schedule
    assert len(request.busy_intervals) == 14
    assert request.query_window.end - request.query_window.start == timedelta(days=7)


def test_small_reproducible_benchmark_counts_slots_without_flaky_time_threshold() -> None:
    report = measure(BenchmarkSize(resources=2, days=1), repetitions=2)

    assert report["slots"] == 16
    assert report["busy_intervals"] == 2
    assert report["iterations"] == 2
    assert report["median_ms"] >= 0
    assert report["peak_traced_kib"] > 0


@pytest.mark.parametrize("resources,days", [(0, 7), (101, 7), (1, 0), (1, 32)])
def test_benchmark_refuses_size_outside_public_limits(resources: int, days: int) -> None:
    with pytest.raises(ValueError):
        BenchmarkSize(resources, days)


def test_benchmark_refuses_zero_iterations() -> None:
    with pytest.raises(ValueError):
        measure(BenchmarkSize(1, 1), repetitions=0)
