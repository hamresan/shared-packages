# hamresan-subscription Roadmap

## Purpose

Build a reusable, pip-installable `hamresan-subscription` package inside `hamresan/shared-packages`.

```text
Repository: hamresan/shared-packages
Package folder: subscription
Distribution: hamresan-subscription
Import: subscription
```

The package is application-agnostic. It does not depend on WordPress, Sellora, Identity, Store, payment providers, or another concrete application. Integrations belong in host composition roots through narrow public contracts.

## Product decisions

- A subject may have at most one active `BASE` subscription at a time.
- Multiple `ADDON` subscriptions may be active concurrently.
- Plans are database-backed and defined by the consuming application through package APIs.
- Subjects use generic `subject_type + subject_id` references and do not require foreign keys to external packages.
- Trials may be time-based, usage-based, recurring-usage-based, or combined.
- Combined trial conditions support `ANY` and `ALL` semantics.
- Entitlements are strongly typed: boolean, integer, decimal, string, or unlimited.
- Entitlement limits and actual usage are separate concepts.
- Usage metrics are generic keys owned semantically by the host application.
- Subscription sources include paid, trial, manual, promotional, and migrated sources.
- Payment processing, invoicing, taxes, and provider-specific billing behavior remain outside this package.

## Architecture principles

- Clean Architecture and SOLID are mandatory.
- Domain and application layers remain framework-independent.
- Application services are small, use-case-oriented orchestrators.
- Validation, mapping, policies, calculations, persistence, and provider integration are separate responsibilities.
- Dependencies are explicit and injected through contracts/interfaces.
- No Service Locator and no hidden dependency construction.
- Public APIs are exported through controlled package boundaries.
- Persistence is async and receives host-owned SQLAlchemy session infrastructure.
- SQLAlchemy engine/sessionmaker lifecycle belongs to the host application.
- Package tables use the `subscription_` prefix.
- Alembic revision history and migration ordering are host-owned.
- Authentication and authorization implementations are host-owned.
- Tests mirror source responsibilities; independent Fakes, Builders, Factories, fixtures, and helpers live in dedicated support files.
- Quality gate: Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%.

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
| 10 | Documentation and release readiness | **NEXT** |

## Stage 0 — Foundation and documentation

Status: **COMPLETED**

Created package foundation, mirrored test structure, packaging metadata, README, Makefile, Ruff, Ruff format, Pyright strict, pytest, and coverage enforcement.

## Stage 1 — Core domain primitives

Status: **COMPLETED**

Implemented generic `SubjectReference`, subscription/plan/trial/usage enums, and strongly typed entitlement value objects. Subject IDs intentionally remain strings so consumers are not forced to use UUID identifiers.

## Stage 2 — Plan and entitlement domain

Status: **COMPLETED**

Implemented `Plan`, `PlanEntitlement`, `PlanCode`, `EntitlementKey`, plan definition rules, and explicit plan status transitions. Pricing/payment concerns remain outside the Plan domain.

## Stage 3 — Trial and usage domain

Status: **COMPLETED**

Implemented generic usage metrics/records/counters, time and usage trial conditions, `TrialPolicy`, and pure `TrialEvaluationPolicy`. Supported scenarios include time-only, usage-only, weekly usage, and combined `ANY`/`ALL` trials.

## Stage 4 — Subscription lifecycle domain

Status: **COMPLETED**

Implemented immutable `Subscription` snapshots, lifecycle transitions, validity evaluation, active-base rules, focused timestamp/state validators, and `SubscriptionLifecycleService`. Cancelled subscriptions are terminal; expired subscriptions may be renewed.

## Stage 5 — Application contracts and use cases

Status: **COMPLETED**

Implemented explicit repositories, Unit of Work, Clock, IdentifierGenerator, DTOs/mappers, and focused use cases for plan management, subscription lifecycle, usage recording/query, trial evaluation, and entitlement resolution.

Application services depend only on contracts and do not depend on SQLAlchemy, FastAPI, Identity, Store, WordPress, or payment implementations.

## Stage 6 — Async SQLAlchemy persistence

Status: **COMPLETED**

Implemented host-session-based async SQLAlchemy repositories and Unit of Work for:

```text
subscription_plan
subscription_plan_entitlement
subscription_subscription
subscription_trial_policy
subscription_trial_usage_condition
subscription_usage_record
```

The host owns engine/sessionmaker lifecycle. External subject references have no foreign keys to Identity, Store, Organization, or other packages.

Stage 9 integration testing exposed that SQLite drops timezone metadata even for `DateTime(timezone=True)`. Persistence was hardened with a dedicated `UtcDateTime` SQLAlchemy type that normalizes aware values to UTC, rejects naive writes, and rehydrates timezone-aware UTC values across dialects. Subscription and Usage timestamps use this type, with mirrored regression tests.

## Stage 7 — Host-owned Alembic integration

Status: **COMPLETED**

Public migration integration exposes:

```text
SUBSCRIPTION_TABLE_PREFIX
subscription_metadata()
include_subscription_name()
```

The host owns `alembic.ini`, `env.py`, revision files, ordering, and the revision graph. The package does not ship an independent Alembic environment.

## Stage 8 — FastAPI adapter

Status: **COMPLETED**

Implemented package-owned presentation boundaries and host-provided security integration:

```text
AuthenticatedActor
AuthenticatedActorDependency
SubscriptionAuthorizer
PlanManagementGuard
SubjectAccessGuard
SubscriptionResourceAccessGuard
FastApiSubscriptionAdapter
build_fastapi_subscription_adapter()
SubscriptionRouterFactory
```

HTTP responsibilities include plan management, subscription creation/read/lifecycle operations, usage record/query, and entitlement queries. Request/response schemas and presentation mappers are separate components. Routes remain thin and never access repositories directly.

Lifecycle endpoints resolve the persisted subscription and authorize its actual subject before mutation. Identity roles, tokens, claims, and authentication implementations remain outside the package.

## Stage 9 — Consumer integration example

Status: **COMPLETED**

Added a real host application under:

```text
examples/subscription_consumer
```

The example demonstrates:

- host-owned async SQLAlchemy engine/sessionmaker;
- host-owned Alembic configuration and environment;
- typed host adapter for the Alembic name-filter callback;
- host implementation of `AuthenticatedActorDependency`;
- host implementation of `SubscriptionAuthorizer`;
- explicit composition of real Subscription domain policies, application use cases, SQLAlchemy Unit of Work, and FastAPI adapter;
- database-backed `BASE` and `ADDON` plans;
- combined `14 days OR 100 conversations` trial;
- generic usage recording;
- manual add-on grant;
- paid activation and renewal after a verified external payment event;
- typed entitlement resolution;
- dedicated `PaidSubscriptionEventHandler` in host code rather than payment logic inside the package.

A dedicated workflow was added:

```text
.github/workflows/subscription-consumer-integration-ci.yml
```

It installs the real package and consumer example and runs the example's `make check`.

The integration flow caught the SQLite timezone round-trip issue described in Stage 6, proving the example acts as a real cross-layer test rather than a documentation-only sample.

Final Stage 9 package quality result:

```text
Ruff: PASS
Ruff format: PASS
Pyright strict: 0 errors
pytest: 203 passed
branch coverage: 93.40%
Subscription Consumer Integration CI: PASS
```

## Stage 10 — Documentation and release readiness

Status: **NEXT**

Finalize release-quality package documentation and distribution readiness:

- replace conceptual README snippets with copyable examples using the final public APIs;
- document direct application-service usage;
- document FastAPI adapter composition;
- document host authentication/authorization integration;
- document SQLAlchemy session ownership;
- document host-owned Alembic integration;
- document BASE/ADDON plan creation;
- document time-, usage-, and combined-trial flows;
- document usage recording and entitlement evaluation;
- document manual/promotional/paid lifecycle integration without embedding payment-provider logic;
- document table ownership and UTC timestamp persistence behavior;
- review public package exports and dependency extras;
- validate wheel/sdist build and clean-install smoke tests;
- finalize version/release checklist and CI expectations.

## Deferred / separate concerns

These remain outside `hamresan-subscription` unless a future concrete requirement changes the boundary:

- payment processing and payment-provider SDKs;
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

## Continuation checkpoint

```text
Implemented: Stages 0–9
Next objective: Stage 10 — Documentation and release readiness
Core decisions: one active BASE per subject; multiple ADDONs; DB-backed consumer-defined plans; typed entitlements; time/usage/combined trials; generic usage metrics; immutable subscription snapshots; explicit contracts/UoW; host-owned async SQLAlchemy sessions; host-owned Alembic graph; host-provided authentication/authorization; payment integration outside the package; UTC-aware persistence across dialects; no hard dependency on other Hamresan packages
Quality gate: Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%
