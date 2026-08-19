# hamresan-subscription Roadmap

## Purpose

Build a reusable `hamresan-subscription` package inside `hamresan/shared-packages`.

The package is generic and application-agnostic. It must be installable with pip and usable by different projects without depending on WordPress, Sellora, Identity, Store, payment providers, or any concrete application implementation.

```text
Repository: hamresan/shared-packages
Package folder: subscription
Distribution: hamresan-subscription
Import: subscription
```

## Product decisions

- A subject may have at most one active `BASE` subscription at a time.
- Multiple `ADDON` subscriptions may be active at the same time.
- Plans are database-backed and managed by the consuming project through package APIs.
- Trials may be time-based, usage-based, recurring-usage-based, or combined.
- Combined trial conditions may use `ANY` or `ALL` completion semantics.
- Entitlements are strongly typed: boolean, integer, decimal, string, or unlimited.
- Entitlement limits and actual usage are separate concepts.
- Subscription sources include paid, trial, manual, promotional, migrated, and future sources.
- Payment processing is outside this package.
- Subjects are generic references and do not require foreign keys to User, Store, Organization, or other package tables.
- Integrations with other Hamresan packages happen through public contracts and host composition roots.

## Architecture principles

- Clean Architecture and SOLID are mandatory.
- Domain and application layers remain framework-independent.
- Application services stay thin and use-case oriented.
- Validation, mapping, policy evaluation, calculations, persistence, and external integration live in dedicated components.
- No service locator and no hidden dependency construction.
- Dependencies are injected through explicit contracts/interfaces.
- Public package APIs are exported through controlled `__init__.py` boundaries.
- Avoid heavy barrel imports and circular dependencies.
- Persistence is async and receives host-owned session infrastructure.
- SQLAlchemy engine/sessionmaker lifecycle belongs to the consuming application.
- Package-owned tables use the `subscription_` prefix.
- Alembic revision history is host-owned.
- Tests mirror source responsibilities.
- Independent Fakes, Builders, Factories, fixtures, and test helpers live in dedicated support files.
- Quality gate: Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%.

## Target structure

```text
subscription/
├── src/subscription/
│   ├── domain/
│   │   ├── entities/
│   │   ├── enums/
│   │   ├── value_objects/
│   │   ├── policies/
│   │   ├── validators/
│   │   └── services/
│   ├── application/
│   │   ├── contracts/
│   │   ├── dto/
│   │   ├── services/
│   │   ├── validators/
│   │   └── mappers/
│   ├── infrastructure/
│   │   └── persistence/sqlalchemy/
│   ├── presentation/
│   │   ├── dependencies/
│   │   ├── errors/
│   │   ├── mappers/
│   │   ├── routes/
│   │   └── schemas/
│   └── migrations/
├── tests/
│   ├── domain/
│   │   ├── policies/
│   │   └── validators/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   ├── migrations/
│   └── support/
├── pyproject.toml
├── Makefile
├── README.md
└── ROADMAP.md
```

## Stage 0 — Foundation and documentation

Status: **COMPLETED**

Completed package foundation, mirrored tests, README, packaging metadata, Ruff, Ruff format, Pyright strict, pytest, and branch coverage >= 85%.

## Stage 1 — Core domain primitives

Status: **COMPLETED**

Implemented and tested:

```text
SubjectReference
SubscriptionType
SubscriptionSource
SubscriptionStatus
PlanStatus
EntitlementValueType
TrialCompletionMode
UsagePeriod
BooleanEntitlementValue
IntegerEntitlementValue
DecimalEntitlementValue
StringEntitlementValue
UnlimitedEntitlementValue
```

Key decisions:

- `SubjectReference` uses generic `subject_type + subject_id`.
- `subject_type` must already be canonical lowercase; no hidden normalization occurs in the domain.
- `subject_id` is a string and does not require UUID format.
- typed entitlement values use separate value-object types rather than `Any` payloads.

## Stage 2 — Plan and entitlement domain

Status: **COMPLETED**

Implemented and tested:

```text
Plan
PlanEntitlement
PlanCode
EntitlementKey
PlanDefinitionPolicy
PlanStatusTransitionPolicy
```

Rules:

- plan code is a stable canonical identifier;
- plan-code uniqueness across persisted plans belongs to repository/application workflows;
- plan type is `BASE` or `ADDON`;
- duplicate entitlement keys inside a Plan are rejected;
- plan lifecycle transitions are explicit;
- retired plans cannot return to active/inactive state;
- pricing/payment concerns remain outside the Plan domain.

## Stage 3 — Trial and usage domain

Status: **COMPLETED**

Implemented and tested:

```text
UsageMetric
UsageRecord
UsageCounter
TimeCondition
UsageCondition
TrialPolicy
TrialEvaluationPolicy
TrialCompletionMode: ANY | ALL
UsagePeriod
```

Supported scenarios include 14-day trials, usage-only trials, combined time/usage trials, weekly usage limits, and `ALL` completion mode.

Rules and boundaries:

- the package does not know what a usage metric means;
- consumers define canonical metric keys;
- `UsageRecord` represents an immutable usage event;
- `UsageCounter` represents aggregate consumption for one metric and period;
- `TrialEvaluationPolicy` is pure and performs no persistence, clock, or external-service calls;
- missing counters are treated as zero usage;
- `ANY` completes when the first configured condition is met;
- `ALL` completes only when every configured condition is met.

## Stage 4 — Subscription lifecycle domain

Status: **COMPLETED**

Implemented and tested:

```text
Subscription
SubscriptionStatusTransitionPolicy
SubscriptionValidityPolicy
ActiveBaseSubscriptionPolicy
SubscriptionDefinitionValidator
SubscriptionTimelineValidator
SubscriptionStateValidator
TimestampOrderValidator
TimezoneAwareDatetimeValidator
SubscriptionLifecycleService
```

Lifecycle behavior includes:

- pending subscription creation snapshots;
- trial start;
- activation;
- cancellation;
- expiration;
- extension;
- renewal of active subscriptions;
- reactivation of expired subscriptions through renewal;
- validity evaluation;
- source tracking;
- base/add-on classification;
- lifecycle timestamps.

Rules and boundaries:

- `Subscription` is an immutable domain snapshot;
- lifecycle mutations are applied by `SubscriptionLifecycleService` and return a new snapshot;
- validation is kept under `domain/validators`, not mixed into decision policies;
- `SubscriptionDefinitionValidator` composes focused timeline and state validators;
- timestamp timezone and ordering rules are handled by dedicated validators;
- decision policies retain only actual domain decisions and do not own structural validation;
- lifecycle services receive policies/validators through explicit dependency injection;
- cancelled subscriptions are terminal;
- expired subscriptions may be renewed back to active;
- trial completion remains the responsibility of `TrialEvaluationPolicy` and is supplied to validity evaluation as a fact;
- a `TRIALING` BASE subscription occupies the same subject-level BASE slot as an `ACTIVE` BASE subscription;
- `ActiveBaseSubscriptionPolicy` is pure and does not query repositories;
- the future application layer must load current subscriptions and pass them to the policy;
- no entity or domain service depends on persistence, Identity, Store, WordPress, FastAPI, or payment implementations.

## Stage 5 — Application contracts and use cases

Status: **NEXT**

Add explicit contracts and use cases for:

```text
Plan Management
Subscription Lifecycle
Entitlement Evaluation
Usage Metering
```

Expected boundaries include repositories, Unit of Work, Clock, IdentifierGenerator, Plan workflows, Subscription lifecycle workflows, entitlement checks, usage recording, and trial evaluation.

Stage 5 must orchestrate the Stage 1–4 domain through explicit contracts. Repository lookups, uniqueness checks, active-BASE checks, current usage loading, and transaction boundaries belong here rather than inside entities or domain services.

## Stage 6 — Async SQLAlchemy persistence

Add async SQLAlchemy persistence using a host-provided session factory.

Rules:

- no global engine/sessionmaker;
- no foreign keys to Identity/Store/Organization tables;
- external subject references use generic type + identifier values;
- package tables use the `subscription_` prefix;
- mapping stays outside services/entities;
- async integration tests are required.

Persistence shape must follow the actual domain from Stages 1–5.

## Stage 7 — Host-owned Alembic integration

Expose package metadata/filter helpers while keeping the revision graph in the host application.

Expected public API:

```text
subscription_metadata()
include_subscription_name()
```

Real Alembic autogenerate tests must verify `subscription_*` ownership/filtering.

## Stage 8 — FastAPI adapter

Add presentation adapters only after the application API is stable.

Potential HTTP responsibilities:

```text
Plan management
Subscription read/manage operations
Entitlement queries
Usage recording/query operations
```

Authentication/authorization remains host-provided. Routes stay thin and mapping/error/dependency responsibilities remain separate.

## Stage 9 — Consumer integration examples

Add a real host example covering plan definition, base/add-on subscriptions, usage recording, typed entitlement checks, combined trials, manual grants, paid activation/renewal after an external payment event, optional composition with other reusable packages, and host-owned SQLAlchemy/Alembic wiring.

## Stage 10 — Documentation and release readiness

Finalize copyable README usage flows, public APIs, persistence/Alembic/FastAPI integration, table ownership, quality commands, and release checks.

## Deferred / separate concerns

These remain outside `hamresan-subscription` unless a future concrete requirement changes the boundary:

- payment processing;
- Stripe or other billing-provider adapters;
- invoicing;
- WordPress connection/authentication;
- tax/VAT calculation;
- application-specific product catalogs;
- user/store/organization persistence;
- notification delivery;
- application-specific authorization roles.

## GitHub quality gate

`.github/workflows/subscription-ci.yml` runs on Subscription pull requests and executes:

```bash
cd subscription
make check
```

This validates Ruff, Ruff format, Pyright strict, pytest, and branch coverage >= 85% before the change is considered merge-ready.

To make GitHub technically block merging when this job fails, the repository's `main` branch/ruleset must mark the `Subscription CI / check` status check as required.

## Continuation checkpoint

```text
Implemented: Stages 0, 1, 2, 3, 4
Next objective: Stage 5 — application contracts and use cases
Core decisions: one active BASE per subject; multiple ADDONs; DB-backed consumer-defined plans; typed entitlements; time/usage/combined trials; generic usage metrics; immutable subscription snapshots; paid/manual/promotional/etc. sources; no hard dependency on other Hamresan packages
Quality gate: Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%
```
