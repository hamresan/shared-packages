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

## Current status

Completed and merged:

- Stage 0 — Source inventory.
- Stage 1 — Package foundation.
- Stage 2 — Core domain.
- Stage 3 — Application contracts and Create/Read use cases.

Stage 4 — SQLAlchemy persistence has been reported as tested and merged in the working flow. At the time this roadmap was updated, GitHub's remote `main` view had not yet exposed the expected `store.infrastructure` tree, so remote verification is still pending before treating the persistence tree as the source of truth for later stages.

Current implementation branch:

```text
agent/add-store-fastapi-adapter
```

Current objective:

```text
Stage 5 — FastAPI adapter
```

## Source observations

The Sellora Store module owns store identity, owner reference, profile and business type, localization, languages, address, contacts, currencies and manual exchange rates, timezone and weekly working schedule, setup status, owner-controlled availability, administrative moderation, soft deletion/restoration, and readiness evaluation.

It explicitly does not own authentication, catalog, channels/provider credentials, inventory, customers, carts/orders, payments, subscriptions, or messaging delivery.

The reusable package removes Sellora-specific composition coupling. In particular, Store must not import Identity FastAPI authorization dependencies directly.

## Package goals

- Clean Architecture and SOLID throughout.
- FastAPI only in the presentation adapter.
- Async SQLAlchemy persistence with a host-provided `AsyncSessionFactory`.
- Package-owned tables use the `store_` prefix.
- Explicit public contracts and controlled exports.
- No direct dependency on Sellora.
- No direct dependency on concrete Identity, Notification, Subscription, Catalog, Messaging, or Channel implementations.
- Host-owned Alembic revision graph.
- Mirror test structure.
- Ruff, Pyright strict, pytest and branch coverage >= 85%.
- No hidden dependency construction inside services.
- Thin use-case services; mapping, validation, policies, persistence, authorization, time and identifiers remain dedicated responsibilities.

## Naming decision

```text
Directory: store/
Python package: store
Distribution: hamresan-store
```

Use `Store` as the core domain name rather than `Business` for the initial reusable package.

## Core domain

Current Store aggregate includes the reusable store-owned state required for the first package release, including:

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
- suspension fields
- deleted_at
- created_at
- updated_at
```

Domain remains dependency-free: no SQLAlchemy, FastAPI, Pydantic, Identity or Sellora imports.

### Core invariants

- Store name is required and normalized.
- Primary language is required.
- Primary language must exist in supported languages.
- Supported languages are unique.
- Country code is normalized and validated as a two-character code.
- Currency codes are normalized and validated as three-character codes.
- Timezone, when present, is a valid IANA timezone identifier.
- Availability is separate from moderation state.
- Soft deletion is separate from availability/moderation.
- Suspension reason `other` requires a description.

## Application layer decisions

The reusable application layer now uses explicit contracts for:

```text
StoreRepository
StoreUnitOfWork
StoreUnitOfWorkFactory
Clock
StoreIdentifierGenerator
```

Implemented first-use-case surface:

```text
CreateStoreCommand
CreateStoreService
GetStoreQuery
GetStoreService
GetOwnedStoreQuery
GetOwnedStoreService
```

The create flow is deliberately split into independent responsibilities:

```text
CreateStoreService
    -> CreateStoreCommandValidator
    -> StoreOwnershipPolicy
    -> StoreFactory
    -> StoreRepository / StoreUnitOfWork
```

The service remains an orchestrator and does not perform persistence, validation or entity construction internally.

## Ownership model

The first release keeps one Store per owner as the default behavior, but this rule is not hard-coded into the service or persistence model.

It is represented through `StoreOwnershipPolicy`, allowing later multi-store support without rewriting unrelated use cases.

The trusted owner ID must come from the authenticated host context. Public create-store request bodies must not be trusted to supply an arbitrary owner ID.

## Cross-package boundaries

### Identity

Store must not import Identity presentation code or concrete authentication implementations.

For FastAPI integration, the host should provide a dependency or adapter that resolves an authenticated actor with the minimum Store-owned contract, conceptually:

```text
AuthenticatedActor
- user_id: UUID
```

`hamresan-identity` can be adapted to this contract in the host composition root.

### Notification

No Notification dependency is currently required by Store.

### Subscription

No direct Subscription dependency is allowed. Future plan/capability checks should use an entitlement/capability contract.

### Catalog / Messaging / Channels

Future readiness checks must use explicit reader/checker contracts and must never read another module's persistence directly.

## Persistence design

Target persistence architecture:

```text
Host AsyncSessionFactory
        ↓
SqlAlchemyStoreUnitOfWork
        ↓
SqlAlchemyStoreRepository
        ↓
SQLAlchemy model
        ↕
Store persistence mapper
        ↕
Store domain aggregate
```

Rules:

- Package never creates a global engine/sessionmaker.
- Session lifecycle comes from the host.
- Persistence logic stays outside services.
- Domain/model conversion belongs to a mapper.
- `owner_user_id` is an external UUID reference and must not create a database FK to Identity tables.
- Store-owned tables use the `store_` prefix.
- Extensible statuses/types are stored as strings rather than PostgreSQL enums.
- Structured values may use JSON/JSONB persistence while remaining explicit typed domain objects.

Expected main table naming:

```text
store_stores
```

Remote verification of the merged Stage 4 tree is still pending as noted in Current status.

## Migration integration

Stage 6 will follow the same host-owned approach as Identity:

- expose Store metadata via public `store.migrations` API;
- expose an `include_store_name` helper;
- optionally expose a migrations extra;
- do not ship an independent package revision root;
- the consuming application owns Alembic revision history and ordering.

## FastAPI adapter design — current stage

Stage 5 must add only presentation responsibilities:

```text
presentation/
├── schemas/
├── mappers/
├── dependencies/
└── routes/
```

Target first HTTP capabilities:

```text
POST /stores
GET  /stores/me
GET  /stores/{store_id}
```

Exact public paths may be adjusted during implementation, but responsibilities must remain separated.

Requirements:

- Request/response schemas use Pydantic.
- Request -> command and domain -> response conversions live in dedicated mappers.
- Routes only translate HTTP input/output and invoke application services.
- No repository or SQLAlchemy access from routes.
- No Store creation logic inside routes.
- No direct Identity imports.
- Authentication is supplied by the host as a dependency/contract.
- Owner ID is taken from the authenticated actor, not the request body.
- Framework dependency call patterns must satisfy Ruff B008 and Pyright strict.
- HTTP errors must be mapped at the presentation boundary rather than leaking persistence details.

Administrative moderation routes remain deferred until the core public FastAPI contract is stable.

## Extraction stages

### Stage 0 — Source inventory

Status: **DONE**

Output:

```text
store/STAGE0_INVENTORY.md
```

Sellora source areas were classified as `REUSE / ADAPT / OMIT / DEFER`.

### Stage 1 — Package foundation

Status: **DONE**

Completed:

- Python 3.12+
- package metadata
- FastAPI / Pydantic / SQLAlchemy dependencies
- Ruff
- Pyright strict
- pytest / pytest-asyncio
- branch coverage >= 85%
- Store CI
- controlled package exports

### Stage 2 — Domain

Status: **DONE**

Completed:

- Store aggregate
- Store enums
- Store value objects
- dedicated validators
- domain behavior tests

### Stage 3 — Application contracts and use cases

Status: **DONE**

Completed:

- repository/UoW contracts
- clock and identifier contracts
- CreateStore use case
- GetStore use case
- GetOwnedStore use case
- CreateStoreCommandValidator
- StoreFactory
- StoreOwnershipPolicy
- mirror application tests and separate test support components

### Stage 4 — SQLAlchemy persistence

Status: **REPORTED TESTED/MERGED — REMOTE VERIFICATION PENDING**

Expected completed behavior:

- host-provided `AsyncSessionFactory`
- `SqlAlchemyStoreRepository`
- `SqlAlchemyStoreUnitOfWork`
- dedicated persistence mapper
- `store_*` table naming
- no FK to Identity tables
- async SQLite integration tests where practical

Before Stage 5 relies on concrete persistence exports, verify these files/classes are visible on remote `main`.

### Stage 5 — FastAPI adapter

Status: **NEXT / IN PROGRESS**

Add:

- authenticated actor contract/dependency boundary
- request schemas
- response schemas
- presentation mappers
- endpoint functions/router installer
- FastAPI integration tests

Keep Identity adaptation in the host composition root.

### Stage 6 — Alembic integration

Status: **PENDING**

Expose Store metadata/filter helpers and add real Alembic autogenerate tests.

### Stage 7 — Consumer integration example

Status: **PENDING**

Create an example composing:

```text
hamresan-identity
hamresan-store
FastAPI
async SQLAlchemy
```

Add Docker testing without a fixed host port.

Notification/Subscription should only be included if an actual Store use case requires them.

### Stage 8 — Documentation and release readiness

Status: **PENDING**

Complete README with installation, composition, session factory wiring, Identity adapter, FastAPI, migrations, public API, table ownership and examples.

Run the full quality gate before final merge/release.

## Test strategy

Tests mirror responsibilities:

```text
tests/
├── domain/
├── application/
├── infrastructure/
├── presentation/
├── migrations/
└── support/
```

Independent Fakes, Builders, Factories and Test Helpers stay in separate support files rather than inside test files/functions.

Quality gate:

```text
Ruff: pass
Ruff format: pass
Pyright strict: 0 errors
Pytest: pass
Branch coverage: >= 85%
```

Coverage should be increased through behavioral tests, not by excluding meaningful production branches.

## Decisions already made

- Sellora remains read-only.
- Shared repository is `hamresan/shared-packages`.
- Package is `hamresan-store` / `store`.
- FastAPI is a presentation adapter only.
- SQLAlchemy persistence is async.
- Database session factory is injected by the host.
- Store-owned tables use the `store_` prefix.
- `owner_user_id` is an external UUID reference, not a DB FK to Identity.
- Clean Architecture, SOLID and explicit DI are mandatory.
- One-store-per-owner is enforced through a replaceable policy.
- No direct concrete Identity dependency.
- No speculative Notification or Subscription dependency.
- Alembic revision graph remains host-owned.
- Tests mirror package structure and coverage must remain >= 85%.

## Deferred capabilities

The following are intentionally not blocking the first reusable Store package:

- admin moderation HTTP surface;
- Sellora-specific readiness orchestration;
- subscription/entitlement enforcement;
- catalog/channel readiness integrations;
- multi-store ownership mode;
- broader Business/Organization aggregate beyond Store.

They should be introduced through stable contracts when a real consumer needs them.

## Continuation checkpoint for a new chat/topic

If the conversation becomes too long, continue from this file.

Use this context:

```text
Repository: hamresan/shared-packages
Roadmap: store/ROADMAP.md
Sellora reference (read-only): hamresan/sellora/backend/app/modules/store
Package: hamresan-store
Completed: Stage 0, Stage 1, Stage 2, Stage 3
Stage 4: reported tested/merged; verify persistence tree on remote main before depending on it
Current branch: agent/add-store-fastapi-adapter
Current objective: Stage 5 — implement FastAPI adapter
Next implementation: authenticated actor boundary + create/read Store schemas, mappers, routes and FastAPI tests
After Stage 5: Stage 6 — host-owned Alembic integration
```

Do not modify Sellora. Keep all implementation work in `shared-packages` on dedicated branches and PRs.
