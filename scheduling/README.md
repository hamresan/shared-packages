# hamresan-scheduling

Reusable calendar management and time-based availability calculation for Python applications.

> **Status: Stage 1 foundation implemented.** The distribution installs and the initial UTC/IANA
> time primitives are tested. Calendar management and the availability engine are **not yet
> implemented**. Follow the independently reviewed stages in [ROADMAP.md](ROADMAP.md).

## Current installation and development

From this directory, run `uv sync --frozen --group dev` and `make check`. The core currently
requires no third-party runtime dependencies on Unix-like systems (and installs `tzdata`
on Windows where the IANA database may be absent). Use `uv build` to produce an sdist and
a wheel.

The first stable, tested primitives are available from `scheduling.domain.time`:

- `IanaTimeZone`: validates and preserves an IANA time zone name.
- `resolve_local_datetime`: converts a calendar-local date and wall time to a zone-aware
  instant; nonexistent DST times fail and ambiguous times require an explicit earlier/later
  choice (the default is rejection).
- `UtcInterval`: a nonempty, half-open `[start, end)` interval of UTC instants with overlap
  and complete-containment checks.

These are foundation primitives, **not** a public API for finding or booking appointments.

## Purpose

`hamresan-scheduling` provides two complementary capabilities:

1. **Calendar Management** — define and update weekly availability, breaks, closures, absences, and date-specific overrides for organizations, locations, and individual resources.
2. **Availability Engine** — calculate possible time slots for a requested activity using relevant calendars, duration, buffers, external busy intervals, and time-window policies.

The package is framework-independent at its core. Persistent calendar management is optional; consuming applications can provide calendar data directly or use an optional async SQLAlchemy adapter. The package is not a universal reservation system, an HR platform, or an authoritative booking database.

## Supported use cases

- An organization defines general operating days, closures, and holidays.
- Multiple locations define different operating hours and IANA timezones.
- Individual resources (people, rooms, equipment, or other schedulable subjects) have their own weekly shifts, breaks, and time off.
- An application requests availability for one or multiple eligible resources, with a specified duration and buffers.
- An application supplies external busy intervals that must be excluded from availability.
- The same API supports one resource or a pool of independently scheduled resources without assuming a shared shift pattern.

## Domain concepts (proposed)

| Concept | Responsibility |
| --- | --- |
| `Calendar` | Identifies a calendar in a trusted tenant scope, with its timezone and owner/scope reference. |
| `WeeklySchedule` | Recurring weekday windows and split shifts. |
| `CalendarException` | Date-specific hours, closure, or override. |
| `BlockedPeriod` | Explicit unavailable interval, such as leave or maintenance. |
| `BusyInterval` | External occupied interval provided by the consuming application. |
| `AvailabilityRequest` | Time range, effective duration, buffers, eligible resources, and relevant policies. |
| `AvailableSlot` | A candidate time interval and, where applicable, the eligible resource ID. |

Organization, location, and resource identifiers are **external references**, not imported entities. The host maps its own organization, branch, staff, or other records into these references. A resource does not have to be a registered user.

For a hierarchical calendar query, the engine combines applicable organization closures, location operating windows, and the resource's own shifts. The exact precedence and intersection rules will be specified and tested before implementation; the engine must not guess how conflicting rules should be applied.

## Calendar rules

The initial engine should support:

- Weekly working windows, including split and overnight shifts.
- Fixed and one-off closures, recurring annual holidays, and date overrides.
- Breaks and temporary unavailable periods.
- IANA timezones and explicit handling of ambiguous or nonexistent DST local times.
- Minimum notice, maximum booking horizon, slot step/interval, activity duration, and optional before/after buffers.
- Per-resource schedules and efficient availability queries over bounded date ranges.
- External busy periods; the calendar package **does not** own the authoritative reservation records.
- Deterministic, machine-readable reasons for unavailable candidate slots where useful.

**Invariant:** A candidate's complete occupied interval, including required buffers, must satisfy applicable working windows and closures. Availability is advisory and can change between search and final reservation.

## Persistence and host integration

The package will offer a small calendar-management application API and two ways to use it:

1. **In-memory/injected adapters:** for tests, lightweight hosts, and callers that already manage their own calendar records.
2. **Optional async SQLAlchemy persistence:** repository and Unit of Work adapters implementing explicit contracts for managed calendars, schedules, and exceptions.

In both modes:

- The **host** owns database connections, async session lifecycle, deployment, and Alembic revision history.
- SQLAlchemy adapters receive a host-supplied session factory. Migrations are composed through public metadata helpers and package-prefixed tables (`scheduling_*`).
- The package never imports host-specific Business, Identity, Employee, or Reservation entities or their persistence models.
- The host supplies trusted tenant and actor scope. Calendar-management use cases enforce authorization through injected contracts/policies rather than trusting arbitrary request fields.
- No built-in queue, scheduler, webhook listener, payment gateway, or external calendar sync worker is required.

## Reservation boundary

`hamresan-scheduling` calculates **candidate** availability; it must never claim to have atomically reserved a resource merely because a slot was returned. The host's authoritative reservation system must revalidate the latest inputs, enforce conflicts and idempotency transactionally, and decide whether creation, cancellation, or rescheduling succeeds.

The package may accept already-booked periods or capacity information from a host-defined reader/adapter, but it does not store bookings, issue booking IDs, own payment holds, or implement a second booking lifecycle.

## Calculation engine implementation decision

The availability engine will be an independent, focused implementation owned by this
package. **Slotify is not a dependency or implementation backend.** Established Python
`datetime` and `zoneinfo` primitives handle date/time representation and timezone rules;
the package owns only its calendar-specific interval composition and slot calculation.
The future engine must pass independently specified golden scenarios, rather than merely
agreeing with another scheduler's output.

## Architecture principles

- Python 3.12+, installable `hamresan-scheduling` distribution with a `src/scheduling/` layout and `pyproject.toml`.
- Framework-independent domain models, deterministic engine, and focused application use cases.
- Explicit contracts and dependency injection; concrete adapters do not leak into services or domain entities.
- Optional integrations (SQLAlchemy, FastAPI, external calendars) stay outside the minimal core and are enabled only when justified.
- Clean Architecture, SOLID, and small responsibility-based components rather than generic managers or registries.
- Time-aware UTC instants internally, preserved IANA zone information, no silent DST guessing.
- Mirrored test folders; dedicated fake repositories, factories, and builders in separate support modules.
- Ruff, strict Pyright, pytest, CI, a committed `uv.lock` and build/install verification.

## Planned public usage

1. The host obtains trusted tenant/owner scope and relevant calendars (either from its own data source or the optional managed persistence adapter).
2. The host determines eligible resources and effective activity duration and supplies current occupied intervals.
3. The availability engine calculates resource-specific candidate slots and returns typed results.
4. The host performs any final reservation through its own authoritative transactional system.

Only the time primitives described under **Current installation and development** are
implemented. No calendar-management operations, slot-query API, or HTTP endpoints are
claimed until their roadmap stages are implemented and tested.
