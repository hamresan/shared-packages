# hamresan-subscription Roadmap

## Purpose

Build a reusable `hamresan-subscription` package inside `hamresan/shared-packages`.

The package is generic and application-agnostic. It must be installable with pip and usable by different projects without depending on WordPress, Sellora, Identity, Store, payment providers, or any concrete application implementation.

Repository layout:

```text
shared-packages/subscription
```

Distribution name:

```text
hamresan-subscription
```

Import package:

```text
subscription
```

## Product decisions

The initial domain baseline is fixed around these rules:

- a subject may have at most one active `BASE` subscription at a time;
- multiple `ADDON` subscriptions may be active at the same time;
- plans are database-backed and are created/managed by the consuming project through package APIs;
- trials are first-class and may be time-based, usage-based, recurring-usage-based, or combined;
- combined trial conditions may use `ANY` or `ALL` completion semantics;
- entitlement values are typed and must support boolean, integer, decimal, string, and unlimited values;
- entitlement limits and actual usage are separate concepts;
- subscriptions may originate from paid, trial, manual, promotional, migrated, or future sources;
- payment processing is outside the package;
- subject ownership is generic and must not require foreign keys to User, Store, Organization, or other package tables;
- integrations with other Hamresan packages happen through public contracts and host composition roots.

## Architecture principles

- Clean Architecture and SOLID are mandatory.
- Domain and application layers remain framework-independent.
- Application services remain thin use-case orchestrators.
- Validation, mapping, policy evaluation, calculations, persistence, and provider-specific integration belong in dedicated components.
- Avoid service locators and hidden dependency construction.
- Dependencies are injected through explicit interfaces/contracts.
- Public package APIs are intentionally exported through controlled `__init__.py` boundaries.
- Avoid heavy barrel imports and circular dependencies.
- Persistence will be async and receive host-owned session infrastructure.
- SQLAlchemy engine/sessionmaker lifecycle belongs to the consuming application.
- Package-owned tables use the `subscription_` prefix.
- Alembic revision history is host-owned.
- Tests mirror source responsibilities.
- Independent Fakes, Builders, Factories, fixtures, and test helpers belong in dedicated support files.
- Quality gate: Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%.

## Target package structure

```text
subscription/
├── src/
│   └── subscription/
│       ├── domain/
│       │   ├── entities/
│       │   ├── enums/
│       │   ├── value_objects/
│       │   ├── policies/
│       │   └── services/
│       ├── application/
│       │   ├── contracts/
│       │   ├── dto/
│       │   ├── services/
│       │   ├── validators/
│       │   └── mappers/
│       ├── infrastructure/
│       │   └── persistence/
│       │       └── sqlalchemy/
│       ├── presentation/
│       │   ├── dependencies/
│       │   ├── errors/
│       │   ├── mappers/
│       │   ├── routes/
│       │   └── schemas/
│       └── migrations/
├── tests/
│   ├── domain/
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

Status: **IN PROGRESS**

Goals:

- create `subscription/` package directory;
- define `hamresan-subscription` packaging metadata;
- create controlled Python package root;
- create clean source layer/package skeleton;
- create mirrored test skeleton;
- configure Ruff, Ruff format, Pyright strict, pytest, and coverage >= 85%;
- document package usage scenarios in README;
- record architectural decisions in this roadmap.

No production business behavior should be implemented in this stage.

## Stage 1 — Core domain primitives

Status: **NEXT**

Define and test framework-independent domain primitives, likely including:

```text
SubjectReference
SubscriptionType
SubscriptionSource
SubscriptionStatus
PlanStatus
EntitlementValueType
TrialCompletionMode
UsagePeriod
```

Define typed entitlement value objects without persistence/framework concerns.

Key decisions to finalize during this stage:

- exact identifier/value validation rules;
- subject-type normalization rules;
- whether plan versions are represented explicitly or by immutable plan revisions;
- subscription status transition vocabulary.

## Stage 2 — Plan and entitlement domain

Implement and test:

```text
Plan
PlanEntitlement
Plan lifecycle/status rules
Entitlement typed values
Plan validation policies
```

Requirements:

- plans are consumer-defined but package-managed;
- plan code must be stable and unique within the package's persistence scope;
- base/add-on type belongs to the plan definition;
- retired/disabled plans remain traceable for existing subscriptions;
- typed values must not rely on unstructured `Any` payloads in the domain.

## Stage 3 — Trial and usage domain

Implement trial policies and usage concepts separately from Subscription orchestration.

Expected concepts:

```text
TrialPolicy
TimeCondition
UsageCondition
CompletionMode: ANY | ALL
UsageMetric
UsageRecord / UsageCounter
UsagePeriod
```

Supported scenarios must include:

```text
14-day trial
100-conversation trial
14 days OR 100 conversations, whichever happens first
50 conversations per week
```

The package remains unaware of what metrics mean. Consumers supply metric keys and record consumption.

## Stage 4 — Subscription lifecycle domain

Implement `Subscription` and its lifecycle rules.

Responsibilities include:

- activation;
- validity evaluation;
- expiration;
- cancellation;
- renewal/extension;
- trial state;
- source tracking;
- base/add-on classification;
- lifecycle timestamps.

Domain policy must enforce at most one active BASE subscription per subject while permitting multiple active ADDON subscriptions.

Avoid embedding repository lookups inside entities. Cross-subscription uniqueness/active-base checks belong in policies/application workflows using repository contracts.

## Stage 5 — Application contracts and use cases

Add explicit contracts and use cases for four bounded responsibilities:

```text
Plan Management
Subscription Lifecycle
Entitlement Evaluation
Usage Metering
```

Likely contracts/use cases:

```text
PlanRepository
SubscriptionRepository
UsageRepository
SubscriptionUnitOfWork
SubscriptionUnitOfWorkFactory
Clock
IdentifierGenerator

PlanCreator
PlanReader
PlanUpdater

SubscriptionCreator
SubscriptionActivator
SubscriptionReader
SubscriptionCanceller
SubscriptionRenewer

SubscriptionValidityChecker
EntitlementChecker

UsageRecorder
UsageReader
TrialEvaluator
```

Exact names should follow the implemented domain rather than forcing speculative abstractions.

Services remain small and use-case oriented. Validators, policies, evaluators, calculators, and mappers are separate components.

## Stage 6 — Async SQLAlchemy persistence

Add async SQLAlchemy persistence using a host-provided session factory.

Expected persistence responsibilities:

```text
SubscriptionBase metadata
Plan models
Plan entitlement models
Subscription models
Trial-policy persistence
Usage persistence
Dedicated persistence mappers
Repositories
Repository factories
Unit of Work
Composition factory
```

Rules:

- no global engine/sessionmaker;
- no FKs to Identity/Store/Organization tables;
- external subject references are stored as generic type + identifier values;
- package-owned table names use `subscription_` prefix;
- mapping stays outside services/entities;
- async integration tests are required.

Persistence shape must be designed from the actual domain produced in Stages 1–5, not guessed in advance.

## Stage 7 — Host-owned Alembic integration

Expose package-owned metadata/filter helpers while keeping the revision graph in the host application.

Expected API:

```text
subscription_metadata()
include_subscription_name()
```

Add optional migration dependency if required:

```bash
pip install "hamresan-subscription[migrations]"
```

Real Alembic autogenerate tests must verify package tables are discoverable and filtering is scoped to `subscription_*` objects.

## Stage 8 — FastAPI adapter

Add presentation adapters after the application API is stable.

Potential HTTP responsibilities:

```text
Plan management
Subscription read/manage operations
Entitlement queries
Usage recording/query operations
```

Authentication/authorization is host-provided. The package should own only narrow actor/authorization boundaries needed by its HTTP adapter and must not import concrete Identity code.

Routes remain thin. Request/response schemas, presentation mappers, error mapping, and dependency contracts are separate components.

Administrative and end-user APIs may be separated if their authorization semantics differ.

## Stage 9 — Consumer integration examples

Add at least one real host composition example showing how a project:

- defines plans;
- attaches a base subscription to its own subject;
- grants add-ons;
- records usage;
- checks typed entitlements;
- handles a usage/time combined trial;
- grants a manual subscription without payment;
- activates/renews a paid subscription after an external payment event;
- combines Subscription with another reusable package through composition rather than persistence coupling;
- wires SQLAlchemy and host-owned Alembic.

The example must demonstrate correct boundaries rather than invent application-specific business logic inside the package.

## Stage 10 — Documentation and release readiness

Finalize README with copyable usage flows for:

- creating/managing plans;
- base subscriptions;
- add-on subscriptions;
- time-based trials;
- usage-based trials;
- combined trials;
- entitlement checks;
- usage metering;
- paid activation;
- manual/promotional grants;
- optional integration with Identity/Store or other packages;
- SQLAlchemy composition;
- FastAPI integration;
- Alembic integration;
- public Python APIs;
- package table ownership;
- quality commands.

Run the complete package and consumer integration quality gates before declaring the `0.1.x` baseline release-ready.

## Deferred / intentionally separate concerns

Unless a concrete consumer requirement changes the boundary, these concerns remain outside the Subscription package:

- payment processing;
- Stripe or other billing-provider adapters;
- invoicing;
- WordPress connection/authentication;
- tax/VAT calculation;
- application-specific product catalogs;
- user/store/organization persistence;
- notification delivery;
- application-specific authorization roles.

External systems may trigger Subscription use cases through public contracts after their own workflows complete.

## Continuation checkpoint

```text
Repository: hamresan/shared-packages
Package folder: subscription
Distribution: hamresan-subscription
Import: subscription
Current objective: Stage 0 — foundation and documentation
Next implementation objective after Stage 0: Stage 1 — core domain primitives
Core decisions: one active BASE per subject; multiple ADDONs; DB-backed consumer-defined plans; typed entitlements; time/usage/combined trials; generic usage metrics; paid/manual/promotional/etc. subscription sources; no hard dependency on other Hamresan packages
Quality gate: Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%
```
