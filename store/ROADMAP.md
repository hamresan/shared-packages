# hamresan-store Roadmap

## Purpose

Create a reusable `hamresan-store` package in `shared-packages` based on the useful, stable parts of Sellora's existing Store module, while keeping Sellora read-only during extraction.

The package should be usable by multiple FastAPI applications without depending on Sellora-specific module paths, composition code, or persistence implementations from another project.

Reference source for analysis only:

```text
hamresan/sellora
backend/app/modules/store
```

Do not modify Sellora as part of this work.

## Source observations

The Sellora Store module currently owns store identity, owner reference, profile and business type, localization, languages, address, contacts, currencies and manual exchange rates, timezone and weekly working schedule, setup status, owner-controlled availability, administrative moderation, soft deletion/restoration, and readiness evaluation.

It explicitly does not own authentication, catalog, channels/provider credentials, inventory, customers, carts/orders, payments, subscriptions, or messaging delivery.

The source is already organized around Clean Architecture concepts with domain entities/value objects/enums, application contracts/services/policies/factories, infrastructure persistence/composition/time/channel adapters, and FastAPI presentation.

A Sellora-specific coupling exists in its current public composition layer: Store imports Identity FastAPI authorization dependencies directly. The reusable package must remove that coupling and depend only on small public authentication/authorization contracts supplied by the host.

## Package goals

The package should provide a focused Store/Business domain that can be reused across products. The first reusable release should keep the minimum valuable behavior while preserving extension points for richer store management later.

Primary goals:

- Clean Architecture and SOLID throughout.
- FastAPI presentation adapter, but no FastAPI-specific logic in domain/application layers.
- Async SQLAlchemy persistence with a host-provided `AsyncSessionFactory`.
- Tables owned by this package use a `store_` prefix.
- Explicit public contracts and controlled package exports.
- No direct dependency on Sellora.
- No direct dependency on concrete Identity, Notification, Subscription, Catalog, Messaging, or Channel implementations.
- Host-owned Alembic revision graph, following the same integration approach used by `hamresan-identity`.
- Mirror test structure, Pyright strict mode, Ruff, pytest, branch coverage, and a minimum 85% coverage gate.
- No hidden dependency construction inside services.
- Services remain thin use-case orchestrators; mapping, validation, policies, persistence, authorization, time, and identifiers stay in dedicated components.

## Naming decision

Package directory and Python package name:

```text
store/
src/store/
```

Distribution name:

```text
hamresan-store
```

Use `Store` as the core domain name rather than `Business` in the first extraction because the Sellora source model and behavior are store-centric. If a future product needs a broader organization/business concept, that should be introduced deliberately rather than making the initial package ambiguous.

## Initial domain scope

### Store aggregate

Target conceptual fields:

```text
Store
- id: UUID
- owner_user_id: UUID
- name
- business_type
- primary_language
- supported_languages
- country_code
- address
- contacts
- base_currency_code
- currencies
- timezone
- working_schedule
- setup_status
- availability_status
- moderation_status
- deleted_at
- created_at
- updated_at
```

The exact representation must be reviewed against the current Sellora implementation before copying any code.

### Core invariants to preserve

- Store name is required and normalized.
- Primary language is required.
- Primary language must exist in supported languages.
- Supported languages must be unique.
- Country code is a validated ISO-style two-character code.
- Currency codes are validated three-character codes.
- Timezone, when present, is an IANA timezone identifier.
- Owner-controlled availability is separate from system/admin moderation state.
- Soft deletion is distinct from moderation/availability.
- Cross-module readiness must be evaluated through contracts, not by reading another module's database.

## Ownership model

Do not hard-code Sellora's "one store per user" rule into an irreversible package design.

For the first release, support enforcing one store per owner as the default persistence/business policy because it matches the current source and immediate consumers. Keep the ownership check behind a dedicated policy/contract so a future multi-store plan does not require rewriting unrelated application services.

The public create-store request must never accept a trusted owner ID from an arbitrary request body. The owner principal comes from a host-supplied authentication context/contract.

## Cross-package boundaries

### Identity

`hamresan-store` must not import Identity presentation dependencies or concrete authentication code.

Define a small Store-owned contract for the authenticated actor, for example conceptually:

```text
AuthenticatedActor
- user_id
```

The host application adapts `hamresan-identity`'s authenticated principal to this contract in its composition root.

Administrative authorization must also be host-supplied through a stable contract such as an `AdminAuthorizer`/`AdminPrincipalProvider`; Store must not own user roles or credentials.

### Notification

No Notification dependency is required for the initial Store extraction unless a concrete Store use case genuinely sends notifications. Do not add it preemptively.

### Subscription

Store may eventually need plan/capability checks, but the first package must not depend directly on a Subscription implementation. Future checks should use a small capability/entitlement contract.

### Catalog / Messaging / Channels

Readiness rules may need external state such as catalog readiness or communication-channel readiness. Represent these as explicit reader/checker contracts. Never access another module's repositories or tables directly.

## Persistence design

Use async SQLAlchemy with a host-provided session factory, following the Identity package approach.

Conceptually:

```text
AsyncSessionFactory
    ↓
Store UnitOfWork / repositories
```

The package must not create a global engine or sessionmaker.

Tables must use the Store prefix. Expected initial table naming should be reviewed from the source before implementation, but all package-owned tables must match:

```text
store_*
```

Prefer regular string columns for extensible statuses/types rather than PostgreSQL enums. Flexible structured data such as address, contacts, currencies, or weekly schedule may use JSON/JSONB in persistence while remaining explicit typed domain objects in application/domain code.

## Migration integration

Use the same host-owned Alembic strategy as Identity:

- expose Store metadata through a public `store.migrations` API;
- provide an `include_store_name` helper for Store-only autogenerate;
- optionally expose an Alembic extra;
- do not ship an independent revision graph with a package-level root revision;
- the consuming application owns migration ordering and revision history.

## Public API target

The exact surface will be finalized after reviewing source implementations. Expected public capabilities include:

```text
StoreModule / StoreModuleConfig
StorePublicApi
CreateStoreCommand / result
StoreReader / OwnedStoreReader
Store profile/settings update use cases
Store availability use cases
Store moderation use cases (optional in first cut after review)
FastApiStoreAdapter
store metadata/migration helpers
```

Only stable consumer-facing contracts should be exported from package `__init__.py` / public modules. Internal SQLAlchemy models, concrete mappers, repository internals, and framework-specific helpers must remain internal unless there is a real integration need.

## Extraction strategy

Do not copy the entire Sellora Store module blindly. Extract behavior in small verified stages.

### Stage 0 — Source inventory

Status: next.

Read Sellora Store only. Produce an inventory of:

- domain entities and value objects;
- enums/statuses;
- repository contracts;
- application services/use cases;
- policies and validators;
- DTOs and mappers;
- persistence models/repositories/UoW;
- FastAPI schemas/routes/dependencies;
- external dependencies and Sellora-specific imports;
- existing tests and coverage-relevant behavior.

Classify each item as:

```text
REUSE
ADAPT
OMIT
DEFER
```

### Stage 1 — Package foundation

Create:

```text
store/
├── pyproject.toml
├── Makefile
├── README.md
├── src/store/
└── tests/
```

Configure:

- Python 3.12+
- FastAPI
- SQLAlchemy async
- Pydantic where presentation schemas require it
- Ruff
- Pyright strict
- pytest / pytest-asyncio
- pytest-cov with branch coverage and 85% minimum
- controlled public package exports

Tests must mirror the source structure under `tests/`.

### Stage 2 — Domain

Extract/adapt core Store aggregate, value objects, enums and domain errors.

Keep the domain dependency-free. No SQLAlchemy, FastAPI, Pydantic, Identity or Sellora imports inside domain objects.

Add focused tests for invariants and state transitions.

### Stage 3 — Application contracts and use cases

Introduce explicit contracts for:

- repositories / UoW;
- authenticated actor / ownership resolution;
- clock;
- identifier generation if needed;
- readiness readers/checkers when actually required.

Extract thin use cases for create/read/update behavior. Separate validators, mappers, policies and factories from services.

### Stage 4 — SQLAlchemy persistence

Add package-owned SQLAlchemy models, mappers, repositories and UoW.

Requirements:

- host-provided `AsyncSessionFactory`;
- `store_` table prefix;
- no persistence logic in services;
- no domain construction hidden in repositories when a mapper/factory has independent responsibility;
- SQLite-compatible integration tests where reasonable, plus PostgreSQL-specific behavior isolated when required.

### Stage 5 — FastAPI adapter

Add request/response schemas, mappers, endpoint callables and router installer.

Authentication and admin authorization come from host-supplied contracts/dependencies. Do not reproduce Sellora's direct import of Identity presentation code.

Avoid large all-purpose update endpoints. Preserve section-based updates where they provide clear domain boundaries.

### Stage 6 — Alembic integration

Expose `store.migrations` metadata/filter helpers and add real autogenerate tests, following the Identity package pattern.

### Stage 7 — Consumer integration example

Create a small example that composes:

```text
hamresan-identity
hamresan-store
FastAPI
async SQLAlchemy
```

Only add Notification/Subscription if the Store package actually needs them by then.

Test the example locally and in Docker without assuming a fixed host port.

### Stage 8 — Documentation and release readiness

Complete README with:

- installation;
- database/session factory wiring;
- Identity adapter composition;
- FastAPI installation;
- migrations;
- public Python API;
- table ownership;
- examples;
- quality commands.

Run full lint, format, strict typecheck, tests, branch coverage and consumer integration CI before merge.

## Test strategy

Tests must mirror package layers and responsibilities. Example target structure:

```text
tests/
├── domain/
├── application/
│   ├── services/
│   ├── policies/
│   ├── validators/
│   └── mappers/
├── infrastructure/
│   └── persistence/
├── presentation/
├── migrations/
└── support/
```

Independent Fake/Builder/Factory/Test Helper responsibilities must live in separate support files, not inside test functions/classes.

Quality gate:

```text
Ruff: pass
Ruff format: pass
Pyright strict: 0 errors
Pytest: pass
Branch coverage: >= 85%
```

Do not raise coverage by excluding meaningful production branches. Add behavioral tests instead.

## Decisions already made

- Sellora is read-only during extraction.
- Shared repository: `hamresan/shared-packages`.
- Package name: `hamresan-store` / Python package `store` unless source inventory reveals a concrete naming conflict.
- FastAPI is supported as a presentation adapter.
- SQLAlchemy async persistence is supported.
- Database session factory is injected by the host.
- Store-owned table names use the `store_` prefix.
- Clean Architecture, SOLID and explicit DI are mandatory.
- No direct concrete dependency on Identity; authentication is adapted through a Store-owned contract.
- No speculative dependency on Notification or Subscription.
- Alembic revision graph remains host-owned.
- Tests mirror package structure with branch coverage >= 85%.

## Open questions to resolve during Stage 0

- Which existing Sellora Store services are sufficiently generic to reuse with only import/path changes?
- Which readiness rules are Sellora-specific and should be deferred behind contracts?
- Whether administrative moderation belongs in the first reusable release or should be a later optional capability.
- Whether contacts/currencies/schedules remain embedded JSON-backed value objects or deserve separate tables in the reusable package.
- Exact initial table layout and indexes.
- Whether the one-store-per-owner rule should be a default policy/configuration option or a hard first-version invariant.
- Which section update endpoints are essential for the first consumer.

## Continuation checkpoint for a new chat/topic

If this conversation becomes too long, continue from this file.

Use this context:

```text
Repository: hamresan/shared-packages
Roadmap: store/ROADMAP.md
Sellora reference (read-only): hamresan/sellora/backend/app/modules/store
Current objective: build reusable hamresan-store package
Next step: Stage 0 — inventory the current Sellora Store module and classify components as REUSE / ADAPT / OMIT / DEFER before implementing code.
```

Do not modify Sellora. Keep all implementation work in `shared-packages` on dedicated branches and PRs.
