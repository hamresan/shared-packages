# hamresan-scheduling — staged implementation roadmap

> **Status:** Stages 1–4 are implemented and tested. Stage 5 optional async SQLAlchemy
> persistence is locally tested, with remote PostgreSQL CI confirmation outstanding.
> Stage 6 optional FastAPI adapter and independent consumer example are implemented
> with HTTP integration tests, pending final consumer/PostgreSQL migration validation.
> Stage 7 release hardening remains.
>
> **Direction:** Calendar Management + Availability Engine, with optional persistence and host-owned infrastructure. Remain reusable across Python applications and independent of their operational domains.

Finish, test, and review each stage before starting the next. Prioritize useful scheduling behavior over speculative abstractions or a full reservation platform.

## Stage overview

| Stage | Focus | Demonstrable result |
| --- | --- | --- |
| **0** | Requirements, library comparison and calendar semantics | Reviewed contracts, precedence rules and bounded proof of concept |
| **1** | Python package foundation | Clean install, quality checks and a small dependency-injection boundary |
| **2** | Calendar domain and validations | Typed weekly schedules, exceptions, closures and timezone rules |
| **3** | Pure availability calculations | Correct per-resource slots, busy intervals, buffers and policies |
| **4** | Calendar management use cases | Create/read/update/archive workflows through repository contracts |
| **5** | Optional async SQLAlchemy persistence | Reusable adapters and host-owned Alembic integration |
| **6** | Optional API adapter and consumer example | Calendar management + availability through a separate host |
| **7** | Hardening, benchmarking and release | Verified correctness, performance and stable public API |

## Stage 0 — Scope and proof of concept

### Work

1. Define a generic external-scope model for organization/location/resource calendars, without importing consuming applications' entities.
2. Define intersection and precedence rules: organization closures, location hours, resource shifts, breaks, date overrides, and blocked periods. Specify what happens when a scope has no calendar.
3. Specify UTC/IANA time handling, overnight windows, DST ambiguity, slot steps, and whether buffers must fit entirely within operating windows.
4. Implement the calculation engine independently, with no `slotify-scheduling` dependency.
   Reuse standard Python `datetime` and `zoneinfo` for time handling and validate the new
   engine against independently specified golden scheduling scenarios.
5. Define the boundary between managed calendar data and externally supplied busy/reservation intervals. Avoid building booking storage or a second reservation lifecycle.
6. Agree on the minimum public inputs/outputs, error codes and tenant-scope requirements; do not create a generic expression language, plugin registry or policy DSL.

### Gate

- [ ] Golden test scenarios and precedence rules are documented and approved.
- [x] Independent calculation engine selected; Slotify excluded as a dependency.
- [ ] Contract and persistence boundaries are agreed before coding.

### Decisions already confirmed

- Preserve the calendar's IANA timezone (for example, `Asia/Muscat` or `Europe/London`).
- Store and compare absolute instants in UTC; define recurring working hours in local time.
- Reject ambiguous or nonexistent local wall times by default at the conversion boundary.
  An explicit earlier/later ambiguity choice is supported for individual instants.
- Use half-open UTC intervals (`[start, end)`) to make adjacent appointments nonconflicting.

The current implementation also records these additional conservative policies:

- Organization closures and location closures veto all resource schedules and overrides.
- Day-specific replacements apply to shifts starting on that local date; hard closed days
  also remove any prior day's overnight shift portion crossing into the closed day.
- Organization, location, and resource calendar snapshots are all explicitly required;
  a missing scope is not treated as open or inherited.
- Ambiguous or nonexistent **recurring window endpoints** raise errors; UTC-stepped slots
  may validly span timezone transitions with two repeated local-hour occurrences.
- Slot-step anchoring at the start of each intersection window is provisional and must
  remain documented until confirmed against real consumers.

The golden tests exercise these policies, but Stage 0's full API and persistence contracts
still need review before management/persistence work.

## Stage 1 — Package foundation

### Work

1. Create `pyproject.toml`, `src/scheduling/`, controlled package exports, typing marker, `uv` lock and reproducible development setup.
2. Establish domain, application/contracts, pure engine, infrastructure/adapters and composition folders only as features need them.
3. Configure Ruff, strict Pyright, pytest with branch coverage, build/install checks and CI.
   Mirror production folders under tests and keep independent test fakes/factories in
   separate modules.
4. Keep the core free from SQLAlchemy, FastAPI and external scheduling providers.

### Gate

- [x] Wheel/sdist build, locked dependency installation, Ruff, strict Pyright, and
      the initial mirrored unit tests pass locally.
- [x] Fresh-environment wheel installation passes locally.
- [ ] Repository CI is verified on GitHub.
- [ ] Dependencies and source/test structure comply with declared boundaries.

## Stage 2 — Calendar rules and domain model

### Work

1. Implement typed `Calendar`, `WeeklySchedule`, working windows, exceptions and blocked periods with explicit validators.
2. Support single and split shifts, intervals crossing midnight, closed dates, annual holidays and date overrides.
3. Define calendar scope, stable identifiers, optional organization/location/resource relationships, and archive semantics without a business-specific model.
4. Normalize and validate timezone-aware data at the application boundary. Reject invalid ranges, overlapping contradictory windows and unsupported local DST times deterministically.

### Gate

- [x] Valid weekly schedules, date overrides, and archived snapshots are represented.
- [x] Invalid windows, timezone settings and contradictory exceptions fail predictably.
- [x] DST gaps/overlaps and overnight shifts have deterministic unit tests.

## Stage 3 — Availability Engine

### Work

1. Implement a pure calculation use case accepting applicable calendar snapshots, requested date range, activity duration, slot interval and policy inputs.
2. Intersect applicable location/organization opening periods with **each resource's own schedule**; do not assume every resource in a pool shares identical working hours.
3. Apply breaks, time off, closures, external busy intervals, and minimum notice/maximum horizon.
4. Include before/after buffers in the full occupied interval and verify that the entire interval is allowed by the applicable calendars.
5. Return typed candidate slots with resource IDs and optional deterministic unavailability reasons. Treat results as advisory; no database writes in calculation code.
6. Keep runtime complexity bounded through date-range limits and a focused benchmark dataset; do not optimize prematurely.

### Gate

- [x] Two differently scheduled resources return resource-specific availability.
- [x] Busy periods, buffers, closures and policy limits affect availability correctly.
- [x] Boundary tests cover buffers, overnight shifts and DST transitions.
- [x] Repeated calculations with identical snapshots and a fixed clock are deterministic.

The calculation is still advisory. Broader performance benchmarking, a consumer example,
and final confirmation of the slot-grid policy remain release gates.

## Stage 4 — Calendar Management use cases

### Work

1. Define repositories and Unit of Work contracts for creating, reading, modifying and archiving calendar configurations.
2. Implement narrow use cases for weekly windows, overrides, closures and blocked periods. Avoid an all-purpose calendar-management service.
3. Accept trusted tenant, actor and scope information from the host; authorize updates and validate scope relationships without depending on the host identity implementation.
4. Add optimistic versioning or equivalent lost-update protection where concurrent calendar editing can cause conflicting changes.

### Gate

- [x] Calendar mutations are validated, tenant-scoped, and tested through injected
      transactional repository/Unit of Work fakes.
- [x] Cross-tenant reads/creates and unauthorized scope mutations fail safely.
- [x] Conflicting edits and duplicate creates are rejected atomically by the test
      contract implementation; optimistic versions cannot silently overwrite updates.

The real SQLAlchemy adapter must enforce the **same atomic CAS and scope/uniqueness
invariants at the database level** in Stage 5. Current fake-backed tests are not a
substitute for PostgreSQL concurrency tests. Public application contracts now include
`CalendarRepository`, `CalendarUnitOfWorkFactory`, and a host-injected
`CalendarAuthorizer`, with verified host actor context.

## Stage 5 — Optional persistence

### Work

1. Add optional async SQLAlchemy 2 models, mappers, repository implementations and Unit of Work adapters for **calendar configuration only**.
2. Inject the host's async session factory; do not create an application-global database engine or own network credentials.
3. Use `scheduling_`-prefixed tables and expose Alembic metadata/filter helpers. The host owns revision files and migration ordering.
4. Keep calculated availability and external reservations out of durable calendar configuration tables; cache only when a real consumer requires it and defines freshness semantics.
5. Test safe concurrency, rollback, archive behavior and tenant isolation in PostgreSQL.

### Gate

- [x] Calendar snapshots round-trip through a real SQL-backed repository across sessions,
      including IANA timezone, exceptions, closures, blocked periods, version and archive state.
- [x] SQL-backed tenant isolation, rollback, duplicate identity rejection and atomic
      compare-and-swap are covered by local integration tests.
- [x] Host-supplied async session factory; SQLAlchemy remains an optional extra and is
      absent from core domain/application imports.
- [x] Real PostgreSQL concurrency and Alembic mixed-metadata integration tests are
      configured as a required separate CI job.
- [ ] Verify that the PostgreSQL CI job executes successfully on the pull-request branch.
- [ ] Verify a consumer-owned Alembic revision/autogenerate-and-upgrade lifecycle with
      a second unrelated application schema (Stage 6 consumer example).

The new SQLAlchemy adapter stores only calendar configuration in
`scheduling_calendars`. PostgreSQL uses JSONB for typed snapshot data, a composite
tenant/calendar primary key, a tenant/scope uniqueness constraint, and a version-guarded
SQL update. No package-owned engine, credentials, migration revision history, or booking
storage were introduced. Local SQLite exercises real SQL transactions; its tests are
not presented as PostgreSQL concurrency proof.

## Stage 6 — Optional FastAPI adapter and consumer example

### Work

1. Provide an optional FastAPI adapter for calendar management and availability queries with strict request/response contracts.
2. Demonstrate a small host that supplies trusted authentication/tenant context, calendar repository configuration and external busy periods.
3. Keep employee details, booking operations, notifications and provider-specific authorization in the host; expose only the minimal subject/scope identifiers needed for scheduling.
4. Test both in-memory and SQLAlchemy-backed composition paths and ensure unavailable resources are not returned as bookable.

### Gate

- [x] A separate example host configures its own SQLAlchemy session factory, API-key
      authentication, authorization, two locations, resources, and database lifecycle.
- [x] All calendar operations are available through optional FastAPI endpoints with
      explicit request/response DTOs, transport mappers, and application use cases.
- [x] Authentication, forbidden scope access, ignored user-supplied tenant fields,
      version conflicts, and invalid schedules are exercised through HTTP requests.
- [x] Independently scheduled resources and externally supplied busy intervals are
      tested through HTTP against both in-memory and real SQL-backed repositories.
- [x] Availability remains advisory; no API endpoint creates or reserves appointments.
- [ ] Confirm a production consumer's own Alembic autogenerate/revision/upgrade path
      against PostgreSQL (remaining Stage 5/6 cross-integration gate).

The FastAPI integration requires the optional `api` extra. `FindAvailability` performs
host-authorized calendar reads and requests authoritative external busy periods through
an injected `BusyIntervalReader`; the endpoint does not trust caller-supplied bookings,
current time, actor, or tenant identity. The example explicitly labels demo API keys
and create-all as unsuitable for production authentication or migration practices.

## Stage 7 — Hardening and release readiness

### Work

1. Run deterministic regression datasets for timezone/DST, overnight windows, resource intersections, closure precedence and occupied-interval buffers.
2. Benchmark a practical range of resources, days, windows and busy intervals; document latency and memory rather than relying on synthetic claims.
3. Review optional dependencies, strict typing, security boundaries, concurrency tests, clean builds, semantic versioning and public exports.
4. Publish release notes only after consumer integration succeeds and README examples match implemented signatures.

### Gate

- [ ] Ruff, format, strict Pyright, pytest, integration tests and package build pass in CI.
- [ ] Two independent host scenarios use the same package without application-specific imports.
- [ ] Boundary and performance benchmarks are recorded with repeatable inputs.

## Deliberately out of scope

- Authoritative appointment/order/reservation creation, cancellation, rescheduling, payments, and idempotent booking writes.
- Employee accounts, HR profiles, contracts, payroll, attendance, or qualifications.
- External calendar-provider synchronization, webhook processing, built-in workers or message queues.
- Generic workflow engines, universal resource-optimization solvers and arbitrary rule scripting.

The package is reusable because it owns a narrow, well-tested scheduling capability — not because it attempts to own every surrounding application concern.
