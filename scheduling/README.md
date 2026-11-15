# hamresan-scheduling

Reusable calendar management and time-based availability calculation for Python applications.

> **Status: design and roadmap only.** This directory does not yet contain an installable package. Follow the independently tested stages in [ROADMAP.md](ROADMAP.md) before relying on any proposed API.

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

## Existing scheduling library assessment

`slotify-scheduling` 0.5.x already provides useful primitives for weekly schedules, overrides, timezone/DST handling, candidate slots, buffers, and resource pools. However, it is pre-1.0, its bundled booking store is synchronous, and resource pools share a slot generator rather than modeling independently scheduled resources. Boundary cases such as buffers extending outside working hours require explicit policy tests.

Stage 0 will compare **reuse behind a small adapter** against a focused implementation of the required calculation primitives. A public package contract must not expose Slotify-specific objects or require it before the proof of concept passes. Use Python's standard `datetime`/`zoneinfo` and mature date/time primitives where they fit; do not rebuild established timezone functionality.

## Architecture principles

- Python 3.12+, installable `hamresan-scheduling` distribution with a `src/scheduling/` layout and `pyproject.toml`.
- Framework-independent domain models, deterministic engine, and focused application use cases.
- Explicit contracts and dependency injection; concrete adapters do not leak into services or domain entities.
- Optional integrations (SQLAlchemy, FastAPI, external calendars) stay outside the minimal core and are enabled only when justified.
- Clean Architecture, SOLID, and small responsibility-based components rather than generic managers or registries.
- Time-aware UTC instants internally, preserved IANA zone information, no silent DST guessing.
- Mirrored test folders; dedicated fake repositories, factories, and builders in separate support modules.
- Ruff, strict Pyright, pytest, CI, reproducible `uv` development locks and build/install verification.

## Planned public usage

1. The host obtains trusted tenant/owner scope and relevant calendars (either from its own data source or the optional managed persistence adapter).
2. The host determines eligible resources and effective activity duration and supplies current occupied intervals.
3. The availability engine calculates resource-specific candidate slots and returns typed results.
4. The host performs any final reservation through its own authoritative transactional system.

No working Python symbols or HTTP endpoints are claimed until their roadmap stages are implemented and tested.
