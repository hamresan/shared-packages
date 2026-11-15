"""CLI benchmark reporting median latency and peak Python allocated memory."""

import argparse
import json
import statistics
import time
import tracemalloc

from scheduling.engine import calculate_availability

from .availability_scenario import BenchmarkSize, make_benchmark_request


def measure(size: BenchmarkSize, *, repetitions: int = 5) -> dict[str, float | int]:
    if repetitions < 1:
        raise ValueError("At least one measured iteration is required.")
    request = make_benchmark_request(size)
    expected = calculate_availability(request)
    durations: list[float] = []
    peaks: list[int] = []
    for _ in range(repetitions):
        tracemalloc.start()
        try:
            start = time.perf_counter()
            result = calculate_availability(request)
            durations.append((time.perf_counter() - start) * 1000)
            _, peak = tracemalloc.get_traced_memory()
            peaks.append(peak)
        finally:
            tracemalloc.stop()
        if result != expected:
            raise RuntimeError("Benchmark became nondeterministic across repeated runs.")
    return {
        "resources": size.resources,
        "days": size.days,
        "busy_intervals": len(request.busy_intervals),
        "slots": len(expected),
        "iterations": repetitions,
        "median_ms": round(statistics.median(durations), 3),
        "peak_traced_kib": round(max(peaks) / 1024, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    for resources, days in ((10, 7), (50, 7), (100, 7), (100, 31)):
        print(json.dumps(measure(BenchmarkSize(resources, days), repetitions=args.runs)))


if __name__ == "__main__":
    main()
