# hamresan-store Roadmap

## Purpose

Build a reusable `hamresan-store` package in `hamresan/shared-packages`, using Sellora's Store module only as a read-only reference.

Reference source:

```text
hamresan/sellora
backend/app/modules/store
```

Sellora must not be modified during this extraction.

## Current status

Implemented through:

- Stage 0 — Source inventory
- Stage 1 — Package foundation
- Stage 2 — Core domain
- Stage 3 — Application contracts and Create/Read use cases
- Stage 4 — Async SQLAlchemy persistence
- Stage 5 — FastAPI adapter

Next objective:

```text
Stage 6 — host-owned Alembic integration
```

## Core architectural decisions

- Clean Architecture and SOLID are mandatory.
- Domain and application layers remain framework-independent.
- FastAPI is only a presentation adapter.
- SQLAlchemy persistence is async.
- The host injects `AsyncSessionFactory`; the package never creates a global engine/sessionmaker.
- Package-owned table names use the `store_` prefix.
- Main Store table is `store_stores`.
- `owner_user_id` is an external UUID reference and has no database FK to Identity tables.
- Store does not import concrete Identity, Notification, Subscription, Catalog, Messaging, or Channel implementations.
- Authentication is adapted at the host composition root.
- One-store-per-owner is enforced by a replaceable `StoreOwnershipPolicy`, not hard-coded into services or persistence.
- Alembic revision history remains host-owned.
- Tests mirror package responsibilities.
- Quality gate remains Ruff + Ruff format + Pyright strict + pytest + branch coverage >= 85%.

## Completed domain

The Store aggregate includes:

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

Core invariants include name normalization, language consistency, country/currency validation, IANA timezone validation, separate availability/moderation/deletion state, and suspension validation.

## Completed application layer

Public application responsibilities include:

```text
StoreRepository
StoreUnitOfWork
StoreUnitOfWorkFactory
Clock
StoreIdentifierGenerator

StoreCreator
StoreReader
OwnedStoreReader

CreateStoreCommand
CreateStoreService
GetStoreQuery
GetStoreService
GetOwnedStoreQuery
GetOwnedStoreService

CreateStoreCommandValidator
StoreOwnershipPolicy
StoreFactory
```

Create flow remains:

```text
CreateStoreService
    -> CreateStoreCommandValidator
    -> StoreOwnershipPolicy
    -> StoreFactory
    -> StoreRepository / StoreUnitOfWork
```

Services remain thin orchestrators.

## Completed persistence layer

Stage 4 uses a host-provided async session factory.

Persistence architecture:

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

Persistence rules:

- no global engine/sessionmaker inside the package;
- no persistence logic in application services;
- mapping is handled by dedicated persistence mappers;
- `store_*` table naming;
- no FK to `identity_users`;
- structured Store data may be persisted as JSON-backed columns while remaining typed domain objects;
- async integration tests are required.

## Cross-package boundaries

### Identity

Store must not import Identity presentation or concrete authentication code.

Store owns the authenticated actor boundary:

```text
AuthenticatedActor
- user_id: UUID
```

The host adapts `hamresan-identity` or another authentication implementation to this contract in its composition root.

### Notification

No Notification dependency is currently required.

### Subscription

No direct Subscription dependency. Future capability checks must use an entitlement/capability contract.

### Catalog / Messaging / Channels

Future readiness checks must use explicit contracts and never access another package's persistence directly.

## Stage 5 — FastAPI adapter

Status: **COMPLETED**

Presentation structure:

```text
src/store/presentation/
├── dependencies/
├── errors/
├── mappers/
├── routes/
├── schemas/
├── factory.py
└── fastapi.py
```

Initial HTTP capabilities:

```text
POST /stores
GET  /stores/me
GET  /stores/{store_id}
```

Implemented requirements:

- Pydantic request/response schemas;
- dedicated request -> command/query and domain -> response mappers;
- thin FastAPI routes;
- no repository or SQLAlchemy access from routes;
- no Store construction logic in routes;
- no direct Identity imports;
- owner ID comes from `AuthenticatedActor`, never from request body;
- extra create-request fields are rejected;
- host-supplied authentication dependency;
- Store-owned `AuthenticatedActor` and authentication dependency types;
- presentation-level error mapping;
- explicit application use-case contracts for presentation DI;
- FastAPI tests under `tests/presentation`;
- presentation Fake/Builder support components under dedicated `tests/support/presentation` files.

Administrative moderation routes remain deferred until the core public HTTP contract is stable.

## Stage 6 — Alembic integration

Status: **NEXT**

Follow the same host-owned strategy used by `hamresan-identity`:

- expose Store metadata via `store.migrations`;
- expose `include_store_name` for Store-only autogenerate;
- optionally provide a migrations extra;
- do not ship a package-owned root revision graph;
- add real Alembic autogenerate tests.

## Stage 7 — Consumer integration example

Status: **PENDING**

Create a real consumer example composing:

```text
hamresan-identity
hamresan-store
FastAPI
async SQLAlchemy
```

Add Docker verification without relying on a fixed host port.

Notification/Subscription should only be added if a concrete Store use case requires them.

## Stage 8 — Documentation and release readiness

Status: **PENDING**

Complete README with:

- installation;
- `AsyncSessionFactory` wiring;
- Identity adapter composition;
- FastAPI setup;
- migrations;
- public Python API;
- table ownership;
- examples;
- quality commands.

Run the complete quality gate before final release readiness.

## Deferred capabilities

The following are intentionally deferred:

- admin moderation HTTP surface;
- Sellora-specific readiness orchestration;
- subscription/entitlement enforcement;
- catalog/channel readiness integrations;
- multi-store ownership mode;
- broader Business/Organization aggregate beyond Store.

They should be introduced only behind stable contracts when a real consumer requires them.

## Continuation checkpoint

If this conversation becomes too long, continue from this file.

```text
Repository: hamresan/shared-packages
Roadmap: store/ROADMAP.md
Sellora reference: hamresan/sellora/backend/app/modules/store (read-only)
Package: hamresan-store
Implemented: Stage 0 through Stage 5
Next objective: Stage 6 — host-owned Alembic integration
Stage 6 requirements: store.migrations metadata + include_store_name + optional Alembic extra + real autogenerate tests
```

Do not modify Sellora. Keep implementation work in `shared-packages` on dedicated branches and PRs.
