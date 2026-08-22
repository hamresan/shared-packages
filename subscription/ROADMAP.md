# hamresan-subscription Roadmap

## Purpose

Build a reusable, pip-installable `hamresan-subscription` package inside `hamresan/shared-packages`.

```text
Repository:   hamresan/shared-packages
Package:      subscription
Distribution: hamresan-subscription
Import:       subscription
```

The package is application-agnostic. Identity, Store, WordPress, payment providers, authentication implementations, authorization rules, and consumer-owned subject models remain outside the package and connect through public contracts at the host composition root.

## Product decisions

- A subject may have at most one active/trialing `BASE` subscription.
- Multiple `ADDON` subscriptions may be active concurrently.
- Plans are database-backed and consumer-defined through package APIs.
- Subjects use generic `subject_type + subject_id` references without foreign keys to external packages.
- Trials support time, usage, recurring usage, and combined `ANY`/`ALL` rules.
- Entitlements are strongly typed: boolean, integer, decimal, string, or unlimited.
- Entitlement limits and actual usage are separate concepts.
- Usage metrics are generic keys whose meaning belongs to the host application.
- Sources include paid, trial, manual, promotional, and migrated subscriptions.
- Payment processing, invoicing, taxes, and provider-specific billing behavior remain outside the package.

## Architecture principles

- Clean Architecture and SOLID.
- Framework-independent domain and application layers.
- Small use-case-oriented application services.
- Explicit dependency injection through contracts/interfaces.
- Separate validation, mapping, policies, persistence, and provider integration.
- No Service Locator or hidden dependency construction.
- Controlled public package APIs.
- Host-owned SQLAlchemy engine/sessionmaker lifecycle.
- Host-owned Alembic revision history and ordering.
- Host-owned authentication and authorization implementations.
- Package tables use the `subscription_` prefix.
- Tests mirror source responsibilities.
- Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%.

## Stage status

| Stage | Scope | Status |
| --- | --- | --- |
| 0 | Foundation and documentation | **COMPLETED** |
| 1 | Core domain primitives | **COMPLETED** |
| 2 | Plan and entitlement domain | **COMPLETED** |
| 3 | Trial and usage domain | **COMPLETED** |
| 4 | Subscription lifecycle domain | **COMPLETED** |
| 5 | Application contracts and use cases | **COMPLETED** |
| 6 | Async SQLAlchemy persistence | **COMPLETED** |
| 7 | Host-owned Alembic integration | **COMPLETED** |
| 8 | FastAPI adapter | **COMPLETED** |
| 9 | Consumer integration example | **COMPLETED** |
| 10 | Documentation and release readiness | **COMPLETED** |

## Stage 0 — Foundation and documentation

Created package foundation, mirrored test structure, packaging metadata, README, Makefile, Ruff, Ruff format, Pyright strict, pytest, and coverage enforcement.

## Stage 1 — Core domain primitives

Implemented generic `SubjectReference`, subscription/plan/trial/usage enums, and strongly typed entitlement value objects. Subject IDs intentionally remain strings so consumers are not forced to use UUID identifiers.

## Stage 2 — Plan and entitlement domain

Implemented `Plan`, `PlanEntitlement`, `PlanCode`, `EntitlementKey`, plan definition rules, and explicit plan lifecycle transitions. Pricing/payment concerns remain outside the Plan domain.

## Stage 3 — Trial and usage domain

Implemented generic usage metrics/records/counters, time and usage conditions, `TrialPolicy`, and pure `TrialEvaluationPolicy`. Supported scenarios include time-only, usage-only, weekly usage, and combined `ANY`/`ALL` trials.

## Stage 4 — Subscription lifecycle domain

Implemented immutable `Subscription` snapshots, lifecycle transitions, validity evaluation, active-base rules, focused timestamp/state validators, and `SubscriptionLifecycleService`.

## Stage 5 — Application contracts and use cases

Implemented explicit repository/UoW/Clock/Identifier contracts, DTOs/mappers, and focused use cases for plan management, subscription lifecycle, usage, trial evaluation, and entitlement resolution.

Application services remain independent from SQLAlchemy, FastAPI, Identity, Store, WordPress, and payment implementations.

## Stage 6 — Async SQLAlchemy persistence

Implemented host-session-based async SQLAlchemy repositories and Unit of Work for:

```text
subscription_plan
subscription_plan_entitlement
subscription_subscription
subscription_trial_policy
subscription_trial_usage_condition
subscription_usage_record
```

Persistence receives host-owned session infrastructure. External subject references have no foreign keys to other packages.

A dedicated UTC SQLAlchemy type normalizes aware values to UTC, rejects naive writes, and rehydrates timezone-aware values across dialect behavior.

## Stage 7 — Host-owned Alembic integration

Public migration integration exposes:

```text
SUBSCRIPTION_TABLE_PREFIX
subscription_metadata()
include_subscription_name()
```

The host owns `alembic.ini`, `env.py`, revision files, ordering, and the revision graph.

## Stage 8 — FastAPI adapter

Implemented package-owned presentation boundaries and host-provided security integration through:

```text
AuthenticatedActor
AuthenticatedActorDependency
SubscriptionAuthorizer
FastApiSubscriptionAdapter
build_fastapi_subscription_adapter()
```

Routes remain thin, subject access is authorized through the host contract, and lifecycle endpoints authorize the persisted subscription's actual subject before mutation.

## Stage 9 — Consumer integration example

Added `examples/subscription_consumer`, demonstrating real host composition for:

- SQLAlchemy engine/sessionmaker ownership;
- Alembic environment/revision ownership;
- authentication and authorization adapters;
- BASE and ADDON plans;
- combined time/usage trial;
- usage recording;
- manual add-on grant;
- paid activation/renewal after a verified external event;
- typed entitlement resolution.

The dedicated consumer workflow runs the example's `make check`. Stage 9 also exposed and drove the UTC persistence hardening described in Stage 6.

## Stage 10 — Documentation and release readiness

Status: **COMPLETED**

Finalized release-quality package guidance and distribution checks:

- README now documents actual public APIs rather than planned/conceptual APIs;
- direct application-service responsibilities are documented;
- SQLAlchemy host-session composition is documented;
- host-owned Alembic integration and table ownership are documented;
- FastAPI authentication/authorization boundaries are documented;
- BASE/ADDON, trial, usage, entitlement, manual/promotional, and paid-event flows are documented;
- UTC timestamp persistence behavior is documented;
- `RELEASE.md` provides versioning, public API, persistence, migration, CI, artifact, publish, and post-release checks;
- `make check` now builds wheel + sdist artifacts;
- `make check` installs the built wheel into an isolated target directory and smoke-tests controlled public imports from the artifact;
- release checks continue to include Ruff, Ruff format, Pyright strict, pytest, and branch coverage >= 85%.

## Deferred / separate concerns

These remain outside `hamresan-subscription` unless a future concrete requirement changes the boundary:

- payment processing and provider SDKs;
- invoicing;
- WordPress connection/authentication;
- tax/VAT calculation;
- application-specific product catalogs;
- user/store/organization persistence;
- notification delivery;
- application-specific authorization roles.

## GitHub quality gates

Package changes run:

```bash
cd subscription
make check
```

Consumer integration changes run:

```bash
cd examples/subscription_consumer
make check
```

Repository branch protection should require the relevant GitHub status checks before merge.

## Roadmap completion checkpoint

```text
Initial roadmap: Stages 0–10 COMPLETED
Package boundary: reusable subscription/plan/trial/usage/entitlement core with optional SQLAlchemy and FastAPI adapters
Persistence: host-owned async sessions; subscription_* tables; UTC-aware timestamps
Migrations: host-owned Alembic revision graph
Security: host-provided authentication and authorization contracts
Billing: payment-provider behavior remains outside the package
Release gate: Ruff + format + Pyright strict + pytest + branch coverage >= 85% + wheel/sdist build + built-wheel smoke import
Next work: only concrete consumer-driven requirements, bug fixes, compatibility changes, or explicit release/version work
```
