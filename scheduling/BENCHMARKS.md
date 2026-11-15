# Scheduling engine repeatable benchmarks

The pure availability calculator is measured with deterministic, application-independent
inputs. No database, HTTP server, Slotify, or cache is used. These numbers are **observed
samples, not guaranteed latency limits or CI performance budgets**.

## Dataset

- Python 3.12, fixed query starting `2026-11-16T00:00:00Z`.
- Explicit organization and location hours, 09:00–17:00 `Asia/Muscat` every day.
- Each resource has its own 09:00–13:00 or 13:00–17:00 shift.
- One external 30-minute occupied interval per resource per day.
- Requested duration 30 minutes, 15-minute steps, and 15-minute buffers on both sides.
- Exact expected slot counts are independently asserted for the smallest dataset.
- Memory measures peak **Python allocations during calculation**, using `tracemalloc`,
  not full process RSS or the preconstructed request graph.

## Reference run

Observed on the isolated execution environment on 15 November 2026, three measured
iterations per dataset, warm-up calculation before measurement:

| Resources | Days | Busy intervals | Slots | Median elapsed (ms) | Peak traced allocations (KiB) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 7 | 70 | 560 | 37.778 | 132.56 |
| 50 | 7 | 350 | 2,800 | 172.089 | 666.22 |
| 100 | 7 | 700 | 5,600 | 355.690 | 1,542.27 |
| 100 | 31 | 3,100 | 24,800 | 1,557.208 | 6,815.72 |

The timings **include tracemalloc instrumentation**, so they should not be compared
directly with uninstrumented production latency. CPU, Python version, load, memory
allocator and workload composition all affect elapsed time. Record hardware and
runtime information alongside a consumer's own measurements before setting an SLO.

## Reproduce

From the `scheduling/` directory:

```bash
uv sync --frozen --group dev
make benchmark
```

For a faster initial measurement:

```bash
uv run --frozen python -m benchmarks.availability_benchmark --runs 3
```

Each JSON line contains resource/day counts, busy interval count, result count,
iteration count, median milliseconds and traced peak KiB. The command uses fixed
inputs and checks output determinism. **No brittle millisecond threshold is used in
pytest/CI.** Performance must be re-evaluated on production-like hosts before release.
