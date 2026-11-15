# hamresan-scheduling

Reusable calendar management and time-based availability calculation for Python applications.

> **Status: Stages 1–4 implemented with in-memory contract tests.** The distribution
> installs, calendar snapshots are validated, the advisory availability engine is pure,
> and authorized calendar-management use cases are implemented. PostgreSQL/SQLAlchemy
> persistence and HTTP integration remain **unimplemented**. See [ROADMAP.md](ROADMAP.md)
> for the outstanding integration gates.

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

The implemented calendar configuration objects are exported from
`scheduling.domain.calendar`. `AvailabilityRequest`, `BusyInterval`, `AvailableSlot`, and
`calculate_availability` are exported from `scheduling.engine`. The engine is purely
computational: it does **not** reserve inventory or fetch authoritative bookings.

## Implemented calendar management API

`scheduling.application.use_cases` exports focused asynchronous operations:

| Use case | Purpose |
| --- | --- |
| `CreateCalendar` | Create one authorized, active calendar at version 1. |
| `GetCalendar` / `ListCalendars` | Read within the actor's trusted tenant and an authorized scope. |
| `UpdateWeeklySchedule` | Replace recurring hours with an expected version. |
| `SetDateException` / `RemoveDateException` | Add, replace or remove a closure/date override. |
| `AddBlockedPeriod` / `RemoveBlockedPeriod` | Update explicit unavailable intervals. |
| `ArchiveCalendar` | Archive without changing stable identity or deleting history. |

The host injects `CalendarUnitOfWorkFactory` and `CalendarAuthorizer` implementations
through contracts exported by `scheduling.application.contracts`. The `TrustedActor`
value in `scheduling.application.models` must be constructed by the **host** from a
verified authentication/tenant context, never from untrusted request fields.

Reads and writes are tenant-scoped. Permission checks use the host-provided authorizer;
it must verify ownership/relationships for external organization/location/resource IDs.
Writes require the caller's `expected_version`; the repository's Unit of Work must enforce
an **atomic compare-and-swap at commit** to prevent lost updates. Management errors
are exported by `scheduling.application.errors`. An archived calendar cannot be modified.

The current test suite supplies a dedicated transactional in-memory fake; it is a test
implementation, **not** a production persistence adapter. Real PostgreSQL concurrency,
transaction rollback, Alembic composition, and migration tests belong to Stage 5.

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

## Domain concepts

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

For a hierarchical calendar query, the engine intersects the organization operating
windows, location operating windows, and **each eligible resource's own** windows in
absolute UTC. An organization or location closure is a hard veto; a resource's hours or
date override cannot reopen its parent scope.

## Implemented calculation semantics

- All three explicit calendar scopes are required; no missing-calendar fallback is guessed.
  The host chooses eligible resources and passes trusted, matching tenant scope. The pure
  engine checks scope and tenant consistency but cannot authenticate the host's actor.
- At a given scope, annual holidays and explicit closed dates take priority over date
  overrides. A non-closure date override replaces that calendar's entire weekly schedule
  for its **start date**. An overnight shift belongs to the date it starts; hard closures
  on the following local day still remove the portion crossing into that closed day.
- Archived calendars expose no availability. Blocked periods and externally supplied busy
  periods remove occupied intervals; the host remains their authoritative source.
- An available candidate's full interval including before/after buffers must fit within
  the intersection of all applicable operating windows and avoid all relevant busy periods.
- Calendar weekdays and local hours use IANA zones; expanded instants and returned slots
  are UTC. Nonexistent/ambiguous local **window endpoints** fail explicitly. UTC stepping
  through a DST transition can correctly produce both distinct occurrences of a repeated
  wall-clock hour or skip a nonexistent one.
- Steps currently begin at the first permissible start of each intersected working
  interval (after the before-buffer), in UTC. This grid-anchoring policy can be revisited
  with consumer feedback; it is not an assumption about fixed wall-clock slot labels.
- The requested search is bounded to 31 days and at most 100 eligible resources; duration
  and step are at least one minute. The full appointment must finish within the requested
  range and maximum horizon, and its start must satisfy minimum notice.

This first engine supports one independently occupied unit per resource. Shared capacity,
resource qualification, inferred calendar inheritance, availability reason codes and
authoritative booking writes are **not** implemented.

## Calendar rules

The current pure engine supports:

- Weekly working windows, including split and overnight shifts.
- Fixed and one-off closures, recurring annual holidays, and date overrides.
- Breaks and temporary unavailable periods.
- IANA timezones and explicit handling of ambiguous or nonexistent DST local times.
- Minimum notice, maximum booking horizon, slot step/interval, activity duration, and optional before/after buffers.
- Per-resource schedules and efficient availability queries over bounded date ranges.
- External busy periods; the calendar package **does not** own the authoritative reservation records.
- Deterministic, machine-readable reasons for unavailable candidate slots are still optional
  future work; current output includes only available candidates.

**Invariant:** A candidate's complete occupied interval, including required buffers, must satisfy applicable working windows and closures. Availability is advisory and can change between search and final reservation.

## Persistence and host integration

The implemented calendar-management application API is designed for two integration modes:

1. **In-memory/injected adapters:** for tests, lightweight hosts, and callers that already manage their own calendar records.
2. **Optional async SQLAlchemy persistence (planned Stage 5):** repository and Unit of Work
   adapters implementing explicit contracts for managed calendars, schedules, and exceptions.

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

The availability engine is an independent, focused implementation owned by this
package. **Slotify is not a dependency or implementation backend.** Established Python
`datetime` and `zoneinfo` primitives handle date/time representation and timezone rules;
the package owns only its calendar-specific interval composition and slot calculation.
The engine must pass independently specified golden scenarios, rather than merely
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

## Public host workflow

1. The host obtains trusted tenant/owner scope and relevant calendars (either from its own data source or the optional managed persistence adapter).
2. The host determines eligible resources and effective activity duration and supplies current occupied intervals.
3. The availability engine calculates resource-specific candidate slots and returns typed results.
4. The host performs any final reservation through its own authoritative transactional system.

The pure slot-query and calendar-management use cases are implemented as described above.
Production database adapters, host authorization implementations, and HTTP endpoints are
deferred until their roadmap stages are implemented and tested.
