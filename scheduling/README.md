# hamresan-scheduling

Reusable calendar management and time-based availability calculation for Python applications.

> **Status: Stages 1–7 implemented; release verification is ongoing.** Calendar management, advisory availability,
> optional SQLAlchemy persistence, optional FastAPI endpoints, and a consumer example
> have automated tests. PostgreSQL integration was reported passing by the consumer;
> the host-owned Alembic lifecycle also passed in the consumer's PostgreSQL tests.
> Remote CI verification remains a release gate.
> Stage 7 regression and benchmark evidence is documented. See [ROADMAP.md](ROADMAP.md).

## Start here

This guide describes the **implemented** package API. It covers installing the library,
calculating slots without infrastructure, managing calendars with the optional SQLAlchemy
adapter, mounting HTTP endpoints, composing Alembic migrations, and verifying integrations.
Python **3.12+** is required. The published distribution name is `hamresan-scheduling`;
the Python import package is `scheduling`. A public PyPI release is **not** assumed.

| If you need to… | Go to… |
| --- | --- |
| Calculate availability from existing calendars | [Pure Python quickstart](#1-calculate-slots-without-a-database) |
| Create and update calendars in a database | [Calendar management](#2-manage-calendars-with-sqlalchemy) |
| Serve the REST API | [FastAPI example](#3-run-the-fastapi-host-example) |
| Add tables to an existing database | [Host-owned Alembic migrations](#4-integrate-host-owned-alembic-migrations) |
| Integrate with a real application | [Production integration checklist](#5-production-integration-checklist) |
| Run tests and diagnose failures | [Verification](#6-verify-the-package) and [Troubleshooting](#troubleshooting) |

### Installation

From the **`shared-packages/` repository root**, install this package into the active
environment of a consuming application:

```bash
# Availability calculator only: no SQLAlchemy or FastAPI dependency.
python -m pip install ./scheduling

# Optional integrations (choose only what your host needs).
python -m pip install './scheduling[persistence]'
python -m pip install './scheduling[api,persistence,migrations]'
```

For installation from a pinned Git commit instead of a local checkout, use the standard
PEP 508 subdirectory notation and replace `<commit-sha>` with a reviewed commit:

```bash
python -m pip install \
  'hamresan-scheduling[api,persistence,migrations] @ git+https://github.com/hamresan/shared-packages.git@<commit-sha>#subdirectory=scheduling'
```

| Extra | Adds | Host must still supply |
| --- | --- | --- |
| Core (none) | Pure domain models and availability engine | Calendars and external booking data |
| `persistence` | Async SQLAlchemy calendar repository and Unit of Work | DB URL, engine, session factory, and a driver such as `aiosqlite` or `asyncpg` |
| `migrations` | Alembic dependency and composable scheduling metadata | Host Alembic project and reviewed revision lifecycle |
| `api` | FastAPI schemas, router, and error handlers | App lifecycle, authenticated actor, authorization, clock, and busy reader |

The minimal runtime has no third-party dependencies on Unix-like systems. On Windows,
`tzdata` provides IANA timezone data if the operating system does not.

For development and all runnable examples in this repository:

```bash
cd scheduling
uv sync --frozen --group dev
```

### 1. Calculate slots without a database

This mode is useful when a host already owns calendar records and only needs deterministic
slot calculation. Execute the [working example](examples/pure_availability.py) from the
`scheduling/` directory:

```bash
uv run --frozen python -m examples.pure_availability
```

It builds three calendar levels in the `Asia/Muscat` timezone: an organization open
09:00–17:00 on Monday, a location open at the same hours, and two separately scheduled
resources (`staff-a` 09:00–11:00; `staff-b` 13:00–15:00). An external busy interval
excludes `staff-a` from 09:30–10:00 local. The query requests 30-minute appointments
on Monday, 2026-11-16, with a 30-minute step.

Expected **UTC** output:

```text
staff-a 2026-11-16T05:00:00+00:00 2026-11-16T05:30:00+00:00
staff-a 2026-11-16T06:00:00+00:00 2026-11-16T06:30:00+00:00
staff-a 2026-11-16T06:30:00+00:00 2026-11-16T07:00:00+00:00
staff-b 2026-11-16T09:00:00+00:00 2026-11-16T09:30:00+00:00
staff-b 2026-11-16T09:30:00+00:00 2026-11-16T10:00:00+00:00
staff-b 2026-11-16T10:00:00+00:00 2026-11-16T10:30:00+00:00
staff-b 2026-11-16T10:30:00+00:00 2026-11-16T11:00:00+00:00
```

The minimal core call looks like this (the example builds these input objects in full):

```python
from datetime import timedelta

from scheduling.domain.time import UtcInterval
from scheduling.engine import AvailabilityRequest, calculate_availability

# organization, location, resources, query_start, query_end and current_utc
# are trusted, correctly typed values supplied by your host.
request = AvailabilityRequest(
    organization=organization,
    location=location,
    resources=tuple(resources),
    query_window=UtcInterval(query_start, query_end),
    duration=timedelta(minutes=30),
    step=timedelta(minutes=15),
    now=current_utc,
)
slots = calculate_availability(request)
```

`Calendar` values are immutable snapshots. A calendar includes `calendar_id`, `tenant_id`,
`scope` (`organization`, `location`, or `resource`), `scope_id`, `timezone=IanaTimeZone(...)`,
and `weekly_schedule=WeeklySchedule(...)`. `DaySchedule.weekday` is `0` for Monday through
`6` for Sunday; `WorkingWindow` times are **naive local wall times**, not UTC. Use
`datetime` values with explicit UTC timezone information in `UtcInterval`. A slot's
`resource_id` is the **external** resource reference, and its interval uses UTC instants.

The host can pass `busy_intervals=(BusyInterval(resource_id, UtcInterval(...)), ...)`,
`buffer_before`, `buffer_after`, `minimum_notice`, and `maximum_horizon`. No network
requests, database reads, or booking writes occur inside `calculate_availability`.

### 2. Manage calendars with SQLAlchemy

Install the `persistence` extra and an async database driver. For SQLite development:

```bash
python -m pip install './scheduling[persistence]' aiosqlite
```

For PostgreSQL, use the `asyncpg` driver and a host-controlled DSN such as
`postgresql+asyncpg://user:password@localhost:5492/database_name`. The `5492` port is
the **host** port if Docker was started with `-p 5492:5432`; `5432` is the container port.

Run the tested [management example](examples/sqlalchemy_management.py) from `scheduling/`:

```bash
uv run --frozen python -m examples.sqlalchemy_management
```

The example uses a disposable in-memory SQLite database. Its actual integration path:

1. The host creates its async engine and `async_sessionmaker`.
2. The host injects a `SqlAlchemyCalendarUnitOfWorkFactory` built with
   `SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper())`.
3. The host derives `TrustedActor(tenant_id, actor_id)` from verified identity, and
   supplies a `CalendarAuthorizer` that checks real scope ownership.
4. `CreateCalendar` creates a calendar at version `1`.
5. `UpdateWeeklySchedule` uses `CalendarMutationGuard` and `expected_version=1` to
   produce version `2` atomically; `GetCalendar` reads the persisted result.

The central composition (taken from the runnable example) is:

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
)

engine = create_async_engine(database_url)
sessions = async_sessionmaker(engine, expire_on_commit=False)
unit_factory = SqlAlchemyCalendarUnitOfWorkFactory(
    sessions,
    SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper()),
)
# Inject unit_factory and your CalendarAuthorizer into application use cases.
# Dispose the engine during the host application's shutdown.
```

Replace the demonstration authorizer with a host implementation of `CalendarAuthorizer`
(`ensure_can_read` and `ensure_can_manage`). Its checks must authenticate the current
tenant and authorize each organization/location/resource reference. The repository's
tenant filtering and optimistic version checks do **not** replace authorization.

For a managed production database, apply Alembic revisions **before** using the
repository. `scheduling_metadata().create_all` is used only by disposable demos/tests.

### 3. Run the FastAPI host example

The tested [consumer application](examples/fastapi_host/README.md) demonstrates a
host-owned API, actor authentication, SQLite persistence, and dependency injection.
From `scheduling/`:

```bash
uv sync --frozen --group dev
export SCHEDULING_DEMO_API_KEY='local-development-secret'
uv run --with uvicorn --frozen \
  uvicorn examples.fastapi_host.app:create_app --factory
```

Open `http://127.0.0.1:8000/docs` for the generated OpenAPI interface. The sample
accepts `X-API-Key: local-development-secret` and only authorizes `org-1`,
`location-1`, `location-2`, `resource-1`, and `resource-2`. In another terminal, set
the same key and create the **three required calendar scopes**:

```bash
export SCHEDULING_DEMO_API_KEY='local-development-secret'

create_demo_calendar() {
  local scope="$1" owner="$2"
  curl --fail-with-body -sS -X POST 'http://127.0.0.1:8000/scheduling/calendars' \
    -H "X-API-Key: ${SCHEDULING_DEMO_API_KEY}" \
    -H 'Content-Type: application/json' \
    --data @- <<JSON
{
  "calendar_id": "calendar-${owner}",
  "scope": "${scope}",
  "scope_id": "${owner}",
  "timezone": "Asia/Muscat",
  "weekly_schedule": {
    "days": [{"weekday": 0, "windows": [{"start": "09:00", "end": "17:00"}]}]
  }
}
JSON
}

create_demo_calendar organization org-1
create_demo_calendar location location-1
create_demo_calendar resource resource-1
```

Next request a **future Monday** (computed at runtime, so the example does not expire)
within the default 31-day search horizon:

```bash
NEXT_MONDAY=$(python -c 'from datetime import UTC, datetime, timedelta; today=datetime.now(UTC).date(); print((today + timedelta(days=((7-today.weekday()) % 7 or 7))).isoformat())')

curl --fail-with-body -sS -X POST 'http://127.0.0.1:8000/scheduling/availability' \
  -H "X-API-Key: ${SCHEDULING_DEMO_API_KEY}" \
  -H 'Content-Type: application/json' \
  --data @- <<JSON
{
  "organization_id": "org-1",
  "location_id": "location-1",
  "resource_ids": ["resource-1"],
  "start": "${NEXT_MONDAY}T00:00:00Z",
  "end": "${NEXT_MONDAY}T23:59:59Z",
  "duration_minutes": 30,
  "step_minutes": 30
}
JSON
```

The JSON response is an array of `{ "resource_id": ..., "start": ..., "end": ... }`
objects in UTC. With the demo schedule, the first Monday slot begins at 09:00 Muscat
time (`05:00Z`). If you rerun the calendar creation commands against the **same** demo
database, a duplicate-scope/ID error (`409`) is expected; use existing records or
reset only the disposable demo database. The sample busy reader returns no bookings.

For example, update the resource's Monday shift after the availability query. The
`expected_version` must equal the latest version returned by a read or mutation:

```bash
curl --fail-with-body -sS -X PUT \
  'http://127.0.0.1:8000/scheduling/calendars/calendar-resource-1/weekly-schedule' \
  -H "X-API-Key: ${SCHEDULING_DEMO_API_KEY}" \
  -H 'Content-Type: application/json' \
  --data '{"expected_version":1,"weekly_schedule":{"days":[{"weekday":0,"windows":[{"start":"10:00","end":"16:00"}]}]}}'
```

On the first successful edit the response includes `"version": 2`. Run this
example only once without changing `expected_version`: retrying version `1` after
the first edit correctly returns `409`.

The FastAPI router provides these routes (all relative to `/scheduling`):

| Method | Path | Request / behavior |
| --- | --- | --- |
| `POST` | `/calendars` | Create `calendar_id`, `scope`, `scope_id`, `timezone`, `weekly_schedule`; optional `exceptions`, `annual_closures`, `blocked_periods`. Returns `201`. |
| `GET` | `/calendars/{calendar_id}` | Read one calendar in the authenticated tenant. |
| `GET` | `/calendars?scope=resource&scope_id=resource-1` | List authorized calendars for one scope/owner pair. |
| `PUT` | `/calendars/{calendar_id}/weekly-schedule` | `{"expected_version":1,"weekly_schedule":{"days":[...]}}`. |
| `PUT` | `/calendars/{calendar_id}/exceptions` | `{"expected_version":1,"exception":{"day":"2026-11-16","closed":true}}`; can instead supply `override_windows` for an open override. |
| `DELETE` | `/calendars/{calendar_id}/exceptions/{YYYY-MM-DD}?expected_version=1` | Remove one local-day exception. |
| `POST` | `/calendars/{calendar_id}/blocked-periods` | `{"expected_version":1,"block":{"start":"2026-11-16T05:00:00Z","end":"2026-11-16T06:00:00Z","reason":"leave"}}`. |
| `DELETE` | `/calendars/{calendar_id}/blocked-periods` | The same versioned `block` body identifies the period to remove. |
| `POST` | `/calendars/{calendar_id}/archive` | `{"expected_version":1}`; archived calendars have no availability and cannot be edited. |
| `POST` | `/availability` | Trusted scope references and UTC `start`/`end`, `duration_minutes`, `step_minutes`; optional buffers, notice, and horizon. |

Error handling: `401` is the demo host's missing/invalid API-key response; `403`
means denied scope access, `404` means missing calendar, `409` means duplicate
calendar/scope or version conflict, and `422` means invalid or unknown request fields
or invalid scheduling values. Production authentication errors are host-defined.

For a real FastAPI host, construct `CalendarHttpDependencies` with your own actor
provider, `Clock`, authorizer-backed use cases, `BusyIntervalReader`, and the exported
`CalendarHttpMapper` and `AvailabilityHttpMapper`; then register:

```python
from scheduling.infrastructure.api.fastapi import (
    create_calendar_router,
    install_calendar_error_handlers,
)

# app: FastAPI; dependencies: CalendarHttpDependencies built by your host.
install_calendar_error_handlers(app)
app.include_router(create_calendar_router(dependencies))
```

The transport uses strict request models. **Never accept `tenant_id` or actor identity
from request JSON**; the host supplies them through verified authentication.

### 4. Integrate host-owned Alembic migrations

Install the `migrations` extra. The scheduling package exposes its table metadata but
does **not** create Alembic versions, run migrations, or own the host's database.
In the host's Alembic `env.py`, compose **both** metadata collections and retain the
package's JSONB rendering hook:

```python
from scheduling.infrastructure.persistence.sqlalchemy import (
    render_scheduling_type,
    scheduling_metadata,
)

# host_metadata is your existing SQLAlchemy metadata.
target_metadata = [host_metadata, scheduling_metadata()]

# In the host's normal Alembic connection/configure block:
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_item=render_scheduling_type,
)
```

If your Alembic `env.py` already has a `render_item` callback, **compose** the callbacks
rather than overwriting host logic: call `render_scheduling_type(kind, value, context)`
first and delegate only when it returns `False`. Preserve any host `include_name` and
`include_object` filters; ensure they do not accidentally exclude `scheduling_*` tables.
The optional `is_scheduling_table(name, kind)` predicate can help compose table filters.

Run the **host's** standard migration workflow, for example:

```bash
alembic revision --autogenerate -m 'add scheduling calendars'
# Review the revision, especially JSON/JSONB types, indexes, and unrelated host tables.
alembic upgrade head
```

The integration suite exercises revision generation, upgrade, and downgrade against
disposable databases. Never use `create_all` as an alternative to reviewed migrations
in production.

### 5. Production integration checklist

- Authenticate each request in the host; derive `TrustedActor` from verified
  authentication and tenant context.
- Authorize each calendar scope and external reference through `CalendarAuthorizer`;
  do not infer access from a matching string ID.
- Map your organization, location, and resource records to the package's scopes. Supply
  an active calendar for **every** queried scope and resource.
- Supply actual occupied intervals via the `BusyIntervalReader` contract (or directly
  to `AvailabilityRequest` for pure use). The provided demo reader is intentionally empty.
- Pass a real UTC clock and store each calendar's original **IANA** timezone name, not
  only a fixed GMT/UTC offset; return UTC instants to clients and localize for display.
- Use `expected_version` from the latest calendar revision on every mutation; handle
  version conflicts by refreshing rather than overwriting another editor's change.
- Recheck availability in your **authoritative booking transaction** before a reservation;
  enforce conflict checks and booking idempotency there. Returned slots are advisory.
- Own engine/session lifecycle, secrets, connection pooling, Alembic revisions, and
  external booking integrations in the host application.

### 6. Verify the package

From `scheduling/`:

```bash
uv sync --frozen --group dev
make check

# Run only the README's executable acceptance examples.
uv run --frozen pytest tests/examples/test_pure_availability.py \
  tests/examples/test_sqlalchemy_management.py --no-cov

# Exercise the FastAPI consumer integration.
uv run --frozen pytest tests/examples/fastapi_host --no-cov

# Build installable wheel and source distribution.
uv build

# Repeatable engine performance scenario.
make benchmark
```

`make check` runs Ruff, format verification, strict Pyright, branch-coverage tests
(threshold **85%**), and build. For an individual test file, append `--no-cov`;
otherwise the full-project coverage threshold is applied to just that subset and can
produce a misleading failure despite passing assertions.

For real PostgreSQL adapter and migration integration tests, use a **disposable** test
database and provide `SCHEDULING_TEST_POSTGRES_URL`:

```bash
docker run -d --name scheduling-test-db \
  -e POSTGRES_USER=scheduling_test \
  -e POSTGRES_PASSWORD=scheduling_test \
  -e POSTGRES_DB=scheduling_test \
  -p 5492:5432 postgres:16

export SCHEDULING_TEST_POSTGRES_URL='postgresql+asyncpg://scheduling_test:scheduling_test@localhost:5492/scheduling_test'
uv run --frozen pytest
```

The fixture can recreate `scheduling_*` test tables: **never point it at a production
or shared database**. With no PostgreSQL URL, those integration cases are skipped.

### Troubleshooting

| Symptom | Likely cause / action |
| --- | --- |
| `ModuleNotFoundError: scheduling` | Install from `./scheduling`, or use `uv run` inside `scheduling/`. The import name is `scheduling`. |
| `ModuleNotFoundError: aiosqlite` or `asyncpg` | Install the async driver in the **host**; SQLAlchemy extras do not choose a database driver. |
| PostgreSQL connection refused on `5432` | With `-p 5492:5432`, connect to `localhost:5492` from the host; use `5432` only inside the Docker network/container. |
| Unknown IANA timezone | Use a valid name such as `Asia/Muscat` or `Europe/London`, and ensure OS zoneinfo/tzdata is installed. |
| Ambiguous/nonexistent local time | DST wall times may map to two or zero instants; resolve ambiguities explicitly or change calendar endpoints. Never silently assume a fixed UTC offset. |
| Availability response is `[]` | Check all three calendars, resource IDs, local weekday/window, UTC query timestamps, active status, notice/horizon, and external occupancy. |
| `403` on demo API | Set the matching `X-API-Key` and use only authorized demo owner IDs; real hosts must check scope ownership. |
| `404` or `409` | Calendar missing in the trusted tenant; or duplicate calendar/scope or stale `expected_version`. Use the current revision and correct identity. |
| `422` validation error | Inspect strict request fields, IANA timezone, UTC datetime format, and valid windows; unknown fields (including `tenant_id`) are rejected. |
| SQLAlchemy reports missing scheduling table | Apply the host's reviewed Alembic migration; `create_all` is only used in disposable examples. |
| Alembic revision contains unresolved `Text()` with JSONB | Include `render_scheduling_type` in `context.configure(render_item=...)`, then regenerate/review the migration. |
| Focused tests pass but coverage fails | Add `--no-cov` to focused runs, then execute the full suite with `make check` to verify coverage. |

## Core concepts and API reference

The stable time primitives are available from `scheduling.domain.time`:

- `IanaTimeZone`: validates and preserves an IANA timezone name.
- `resolve_local_datetime`: converts a calendar-local date and wall time to a zone-aware
  instant; nonexistent DST times fail and ambiguous times require an explicit earlier/later
  choice (the default is rejection).
- `UtcInterval`: a nonempty, half-open `[start, end)` interval of UTC instants with overlap
  and complete-containment checks.

Calendar configuration objects are exported from `scheduling.domain.calendar`.
`AvailabilityRequest`, `BusyInterval`, `AvailableSlot`, and `calculate_availability`
are exported from `scheduling.engine`.

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

The test suite supplies a dedicated transactional in-memory fake and exercises the optional
SQLAlchemy adapter with real SQL transactions. A dedicated PostgreSQL CI job tests concurrent
version conflicts and mixed host/package Alembic metadata.

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
2. **Optional async SQLAlchemy persistence (Stage 5):** repository and Unit of Work
   adapters implementing the same calendar-management contracts.

In both modes:

- The **host** owns database engines, session-factory configuration, deployment, and Alembic
  revision history. A Unit of Work owns and closes each session it obtains from the factory.
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
The host owns authentication and scope authorization; the optional FastAPI transport
adapter is provided in Stage 6.

## Optional SQLAlchemy persistence integration

Install `hamresan-scheduling[persistence]` for the async persistence adapter, or
`hamresan-scheduling[migrations]` for Alembic composition. Neither dependency is loaded by
the pure calculation engine.

The host constructs its own `async_sessionmaker` and injects it into
`SqlAlchemyCalendarUnitOfWorkFactory`, alongside a
`SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper())`. These types are
exported by `scheduling.infrastructure.persistence.sqlalchemy`. The resulting factory
fulfills the public `CalendarUnitOfWorkFactory` contract and can be passed unchanged to
calendar-management use cases. The host's `CalendarAuthorizer` remains mandatory for
authorization; persistence is **not** a substitute for it.

The host adds `scheduling_metadata()` to its Alembic `target_metadata` sequence and
generates/reviews its own revision files. `is_scheduling_table` is an optional table-name
predicate for the host's migration filters; it must be composed with any existing host
filters. When autogenerating the JSONB columns, the host must also supply the exported
`render_scheduling_type` to Alembic's `context.configure(render_item=...)`. This
keeps JSONB variant expressions import-safe in generated revisions, rather than
emitting an unqualified `Text()` reference. A real disposable-host regression test
generates, upgrades and downgrades a revision alongside unrelated host tables on
SQLite; the same acceptance test is configured to run against PostgreSQL in CI.
The package provides **no** auto-running migrations. The table
`scheduling_calendars` has tenant-scoped identifiers and a unique tenant/scope key,
optimistic version checks, JSONB configuration snapshots on PostgreSQL, and an archive
flag. There are no booking, slot-cache, or reservation tables.

For local adapter tests run `uv run --frozen pytest tests/infrastructure/persistence/sqlalchemy`.
To exercise the real PostgreSQL integration suite, set
`SCHEDULING_TEST_POSTGRES_URL=postgresql+asyncpg://...` to a dedicated disposable test
database; the integration fixtures recreate the scheduling tables. The PostgreSQL CI
job provisions its own disposable server.

## Optional FastAPI host integration

Install `hamresan-scheduling[api]` to enable the HTTP adapter. The host supplies all
dependencies to `CalendarHttpDependencies` and mounts `create_calendar_router(deps)` on
its own FastAPI application. Call `install_calendar_error_handlers(app)` once to map
domain/application failures to HTTP status codes. These functions are exported by
`scheduling.infrastructure.api.fastapi`. Importing the pure domain/engine does not
load FastAPI or SQLAlchemy.

Endpoints under `/scheduling` include create/read/list calendars, replace weekly
schedules, set/remove date exceptions, add/remove blocked periods, archive a calendar,
and query advisory availability. Update requests require an `expected_version`.
Requests cannot choose their tenant or authenticated actor: the host injects
`get_actor` and must verify authorization with its `CalendarAuthorizer`. The router
uses dedicated Pydantic DTOs and mappers; no persistence or domain logic lives in
route functions. The host injects a `Clock` for authoritative current time and a
`BusyIntervalReader` for real external booking occupancy, rather than trusting
client-supplied busy periods.

The runnable example under [examples/fastapi_host](examples/fastapi_host/README.md)
uses an authenticated demo principal, two locations, two resources, a host-owned
SQLite/SQLAlchemy session factory, and host-controlled lifecycle. Replace its
demo API key and empty busy reader with production authentication and booking
integration. Run mirrored HTTP acceptance tests with
`uv run --frozen pytest tests/infrastructure/api/fastapi tests/examples`.

## Stage 7 verification and performance

Run `make check` for Ruff, formatting, strict Pyright, full branch-coverage tests and
wheel/sdist build. For a focused subset of tests, use `--no-cov` so the full-project
85% threshold is not mistakenly applied to only one module. With a dedicated
PostgreSQL test database configured in `SCHEDULING_TEST_POSTGRES_URL`, the full test
suite also runs the PostgreSQL integration cases.

Run `make benchmark` to measure the pure availability engine on deterministic pools of
10, 50 and 100 resources across 7 and 31 days. Recorded sample timings and memory
methodology are in [BENCHMARKS.md](BENCHMARKS.md). See
[HARDENING.md](HARDENING.md) for the exact security/dependency audit and outstanding
release blockers. The package is not declared production-ready solely because
branch coverage is high.
