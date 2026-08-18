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
- Stage 6 — Host-owned Alembic integration
- Stage 7 — Consumer integration example

Next objective:

```text
Stage 8 — Documentation and release readiness
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
build_sqlalchemy_store_unit_of_work_factory
        ↓
SqlAlchemyStoreUnitOfWork
        ↓
SqlAlchemyStoreRepositoryFactory
        ↓
SqlAlchemyStoreRepository
        ↓
StorePersistenceMapper
        ↓
StoreModel / StoreBase metadata
```

Persistence rules:

- no global engine/sessionmaker inside the package;
- no persistence logic in application services;
- persistence composition is isolated in the SQLAlchemy infrastructure adapter;
- mapping is handled by dedicated persistence mappers;
- repository construction is handled by a dedicated repository factory;
- `store_*` table naming;
- no FK to `identity_users`;
- structured Store data may be persisted as JSON-backed columns while remaining typed domain objects;
- async integration tests are required.

The reusable persistence implementation follows the real Sellora Store persistence shape as a read-only reference while removing Sellora-specific coupling: no Identity FK, no Sellora base model, and no Sellora module imports.

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

Status: **COMPLETED**

Implemented the same host-owned strategy used by `hamresan-identity`:

- `store.migrations.store_metadata()` exposes Store-owned SQLAlchemy metadata;
- `store.migrations.include_store_name()` filters Store-only reflection/autogenerate;
- `hamresan-store[migrations]` provides the optional Alembic dependency;
- the package does not ship a package-owned/root revision graph;
- real Alembic `compare_metadata` tests verify `store_stores` autogeneration.

Migration ordering, revision IDs, and the revision graph remain owned by the consuming application.

## Stage 7 — Consumer integration example

Status: **COMPLETED**

Added `examples/identity_store_consumer` as a real host composition example for:

```text
hamresan-identity
hamresan-store
FastAPI
async SQLAlchemy
host-owned Alembic
```

The example demonstrates:

- one host-owned async engine/sessionmaker shared through injected session factories;
- Identity -> Store authenticated actor adaptation in the host composition root;
- Store application service/UoW composition without bypassing package contracts;
- Identity and Store FastAPI adapters installed on one application;
- host-owned Alembic metadata/filter wiring for both packages;
- integration tests proving one Identity principal can create/read its Store;
- real combined-metadata Alembic autogenerate tests;
- Docker verification that runs the full example quality gate without publishing a fixed host port;
- dedicated CI for the Identity + Store consumer example.

Notification is present only as the dependency required to compose Identity; Store does not depend on Notification or Subscription.

## Stage 8 — Documentation and release readiness

Status: **NEXT**

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
Implemented: Stage 0 through Stage 7
Next objective: Stage 8 — documentation and release readiness
Stage 8 requirements: complete README/public API/table ownership/examples/quality documentation and run the full release-readiness gate
```

Do not modify Sellora. Keep implementation work in `shared-packages` on dedicated branches and PRs.
