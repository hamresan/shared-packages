# hamresan-store

Reusable Store domain, application, async SQLAlchemy persistence, FastAPI adapter, and host-owned Alembic integration for Python 3.12+ services.

`hamresan-store` is framework-independent in its domain/application core. It does not import Sellora or concrete Identity implementations. Authentication, database engine/session lifecycle, and Alembic revision history remain owned by the consuming application.

## Installation

Install the package normally:

```bash
pip install hamresan-store
```

If the host uses Alembic integration helpers:

```bash
pip install "hamresan-store[migrations]"
```

For local package development:

```bash
make install-dev
```

## Quickstart — using the package in a FastAPI application

A typical host application uses `hamresan-store` in five steps:

1. create the host-owned async SQLAlchemy session factory;
2. compose the Store application services;
3. adapt the host authentication result to `AuthenticatedActor`;
4. build and install the FastAPI adapter;
5. let the host own Alembic migrations.

### 1. Create the database session factory

The host owns the database engine and session lifecycle. Store only receives the session factory.

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from store.infrastructure.persistence import build_sqlalchemy_store_unit_of_work_factory

engine = create_async_engine("postgresql+asyncpg://user:password@localhost/app")
session_factory = async_sessionmaker(engine, expire_on_commit=False)

store_uow_factory = build_sqlalchemy_store_unit_of_work_factory(session_factory)
```

Do not create a second Store-specific database engine when the application already owns one. The same host session infrastructure can be supplied to other reusable packages as well.

### 2. Compose the Store services

The Store package does not hide composition behind a service locator. The host explicitly provides replaceable dependencies such as the clock and identifier generator.

```python
from datetime import UTC, datetime
from uuid import UUID, uuid4

from store import (
    CountryCodeValidator,
    CreateStoreService,
    CurrencyCodeValidator,
    GetOwnedStoreService,
    GetStoreService,
    LanguageSettingsValidator,
    StoreNameValidator,
)
from store.application import (
    Clock,
    CreateStoreCommandValidator,
    StoreFactory,
    StoreIdentifierGenerator,
    StoreOwnershipPolicy,
)


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)


class UuidStoreIdentifierGenerator(StoreIdentifierGenerator):
    def new_store_id(self) -> UUID:
        return uuid4()


create_store_service = CreateStoreService(
    unit_of_work_factory=store_uow_factory,
    validator=CreateStoreCommandValidator(
        name_validator=StoreNameValidator(),
        language_validator=LanguageSettingsValidator(),
        country_validator=CountryCodeValidator(),
        currency_validator=CurrencyCodeValidator(),
    ),
    ownership_policy=StoreOwnershipPolicy(),
    factory=StoreFactory(
        identifier_generator=UuidStoreIdentifierGenerator(),
        clock=SystemClock(),
    ),
)

get_owned_store_service = GetOwnedStoreService(store_uow_factory)
get_store_service = GetStoreService(store_uow_factory)
```

The default `StoreOwnershipPolicy` enforces the current one-store-per-owner rule. A future host can replace that policy without changing the HTTP or persistence layers.

### 3. Adapt authentication to Store

Store does not authenticate tokens itself and does not depend on `hamresan-identity`. The host authentication layer must return Store's small actor contract:

```python
from store import AuthenticatedActor


async def require_store_actor() -> AuthenticatedActor:
    principal = await authenticate_request_with_your_identity_layer()
    return AuthenticatedActor(user_id=principal.user_id)
```

`authenticate_request_with_your_identity_layer()` represents the host application's existing authentication dependency. When using `hamresan-identity`, authenticate through its public API and map the resulting principal to `AuthenticatedActor` in the host composition root.

The important boundary is:

```text
host authentication / hamresan-identity
                ↓
        AuthenticatedActor
                ↓
          hamresan-store
```

`owner_user_id` is therefore never trusted from an HTTP request body.

### 4. Install the FastAPI adapter

Once the use cases and authentication dependency are available, install Store on the host FastAPI application:

```python
from fastapi import FastAPI

from store import build_fastapi_store_adapter

app = FastAPI()

store_adapter = build_fastapi_store_adapter(
    authenticated_actor_dependency=require_store_actor,
    store_creator=create_store_service,
    owned_store_reader=get_owned_store_service,
    store_reader=get_store_service,
)

store_adapter.install(app)
```

The application now exposes:

```text
POST /stores
GET  /stores/me
GET  /stores/{store_id}
```

### 5. Use the HTTP API

Create a Store:

```http
POST /stores
Authorization: Bearer <host-access-token>
Content-Type: application/json

{
  "name": "Acme Store",
  "business_type": "retail",
  "primary_language": "en",
  "country_code": "OM",
  "base_currency_code": "OMR"
}
```

Notice that `owner_user_id` is not part of the request. It is derived from `AuthenticatedActor`.

Read the authenticated user's Store:

```http
GET /stores/me
Authorization: Bearer <host-access-token>
```

Read a Store by ID:

```http
GET /stores/{store_id}
Authorization: Bearer <host-access-token>
```

The create request rejects unknown fields, including attempts to inject a trusted owner ID.

### 6. Add Store metadata to the host Alembic environment

The host owns revision files and ordering. Store only exposes package metadata and an ownership filter:

```python
from alembic import context
from store.migrations import include_store_name, store_metadata

context.configure(
    connection=connection,
    target_metadata=store_metadata(),
    include_name=include_store_name,
    include_schemas=True,
)
```

For an application combining Store with other reusable packages, compose their metadata/filter helpers in the host Alembic layer. See `examples/identity_store_consumer` for the complete Identity + Store example.

## Package boundaries

The package owns:

- Store domain model, value objects, enums, and validators;
- Create/Read application use cases and contracts;
- async SQLAlchemy models, mappers, repository, and Unit of Work adapters;
- Store FastAPI request/response schemas and routes;
- Store-owned Alembic metadata/filter helpers.

The host application owns:

- authentication implementation and Identity integration;
- SQLAlchemy engine and async sessionmaker;
- dependency composition;
- Alembic configuration, revision IDs, ordering, and revision files;
- cross-package orchestration.

`owner_user_id` is an external UUID reference. Store intentionally does not define a database foreign key to Identity tables.

## Async SQLAlchemy wiring

The consuming application creates the engine/sessionmaker and injects the session factory into Store:

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from store.infrastructure.persistence import build_sqlalchemy_store_unit_of_work_factory

engine = create_async_engine(database_url)
session_maker = async_sessionmaker(engine, expire_on_commit=False)

store_uow_factory = build_sqlalchemy_store_unit_of_work_factory(session_maker)
```

The package never creates a global engine or sessionmaker.

The complete consumer example uses a host-owned async context-manager session factory and shares it with Identity without sharing repositories or models. See `examples/identity_store_consumer`.

## Application composition

Create/Read services are composed explicitly. Replaceable concerns such as time and identifier generation are injected through contracts:

```python
from store import (
    CountryCodeValidator,
    CreateStoreService,
    CurrencyCodeValidator,
    GetOwnedStoreService,
    GetStoreService,
    LanguageSettingsValidator,
    StoreNameValidator,
)
from store.application import (
    CreateStoreCommandValidator,
    StoreFactory,
    StoreOwnershipPolicy,
)

create_store_service = CreateStoreService(
    unit_of_work_factory=store_uow_factory,
    validator=CreateStoreCommandValidator(
        name_validator=StoreNameValidator(),
        language_validator=LanguageSettingsValidator(),
        country_validator=CountryCodeValidator(),
        currency_validator=CurrencyCodeValidator(),
    ),
    ownership_policy=StoreOwnershipPolicy(),
    factory=StoreFactory(
        identifier_generator=store_identifier_generator,
        clock=clock,
    ),
)

get_owned_store_service = GetOwnedStoreService(store_uow_factory)
get_store_service = GetStoreService(store_uow_factory)
```

`StoreIdentifierGenerator` and `Clock` are host-provided application contracts. The consumer example contains small production-style implementations using UUID4 and the system UTC clock.

## Authentication and Identity adapter

Store owns only this authenticated boundary:

```python
from store import AuthenticatedActor
```

The host adapts its authentication system to `AuthenticatedActor`. For a host using `hamresan-identity`, the adapter belongs in the host composition root:

```python
principal = await identity_authenticator.authenticate(access_token)
actor = AuthenticatedActor(user_id=principal.user_id)
```

Store does not import `hamresan-identity` and does not know how credentials or tokens are validated.

Create-store requests do not accept `owner_user_id`. The FastAPI adapter derives it from the authenticated actor, and extra request fields are rejected.

## FastAPI setup

The HTTP surface is:

```text
POST /stores
GET  /stores/me
GET  /stores/{store_id}
```

Compose and install the adapter explicitly:

```python
from store import build_fastapi_store_adapter

store_adapter = build_fastapi_store_adapter(
    authenticated_actor_dependency=require_store_actor,
    store_creator=create_store_service,
    owned_store_reader=get_owned_store_service,
    store_reader=get_store_service,
)

store_adapter.install(app)
```

The authentication dependency is host-supplied. Routes remain thin and do not access repositories or SQLAlchemy directly.

## Alembic integration

Alembic revision history belongs to the host application. Store exposes only its metadata and name filter:

```python
from store.migrations import include_store_name, store_metadata
```

For a Store-only Alembic environment:

```python
context.configure(
    connection=connection,
    target_metadata=store_metadata(),
    include_name=include_store_name,
    include_schemas=True,
)
```

A host combining multiple reusable packages keeps one host-owned revision graph and supplies each package's metadata/filter from the composition layer. `examples/identity_store_consumer/migrations/env.py` demonstrates Identity + Store composition.

The package does not ship a root revision graph and does not choose revision identifiers or migration ordering.

## Database table ownership

Store owns database objects whose table names use the `store_` prefix.

Current table ownership:

| Table | Owner | Notes |
| --- | --- | --- |
| `store_stores` | `hamresan-store` | Main Store persistence table |

`owner_user_id` is stored as a UUID value without an Identity foreign key. Other packages must not access Store persistence directly; integration should happen through public contracts/use cases.

## Public Python API

The preferred public imports are intentionally grouped by responsibility.

### Root `store`

Common domain types, Create/Read use cases/contracts, and FastAPI entry points are exported from `store`, including:

```text
AuthenticatedActor
Store
StoreAddress
StoreContact
StoreCurrency
DailyWorkingHours
WeeklyWorkingSchedule
CreateStoreCommand
CreateStoreService
GetStoreService
GetOwnedStoreService
StoreCreator
StoreReader
OwnedStoreReader
StoreRepository
StoreUnitOfWork
StoreUnitOfWorkFactory
FastApiStoreAdapter
build_fastapi_store_adapter
```

### `store.application`

Application composition components and replaceable contracts are exported here, including:

```text
Clock
StoreIdentifierGenerator
CreateStoreCommandValidator
StoreOwnershipPolicy
StoreFactory
```

### `store.infrastructure.persistence`

SQLAlchemy adapter/composition API:

```text
AsyncSessionFactory
SqlAlchemyStoreRepository
SqlAlchemyStoreRepositoryFactory
SqlAlchemyStoreUnitOfWork
SqlAlchemyStoreUnitOfWorkFactory
StoreBase
StoreModel
StorePersistenceMapper
build_sqlalchemy_store_unit_of_work_factory
build_store_persistence_mapper
```

### `store.presentation`

FastAPI-specific boundary:

```text
AuthenticatedActor
AuthenticatedActorDependency
CreateStoreRequest
StoreResponse
FastApiStoreAdapter
build_fastapi_store_adapter
```

### `store.migrations`

Host-owned migration integration:

```text
STORE_TABLE_PREFIX
store_metadata
include_store_name
```

Consumers should prefer these public package APIs rather than importing internal implementation modules.

## Consumer example

`examples/identity_store_consumer` is the reference integration for:

```text
hamresan-identity
hamresan-store
FastAPI
async SQLAlchemy
host-owned Alembic
```

It demonstrates one host-owned engine/sessionmaker, Identity-to-Store actor adaptation, explicit Store service composition, both FastAPI adapters on one application, combined host-owned Alembic configuration, HTTP integration tests, and Docker verification.

From the example directory:

```bash
make check
make docker-test
```

No fixed host port is published by the Docker verification container.

## Architecture rules

- Domain code has no FastAPI, SQLAlchemy, Identity, or Sellora dependencies.
- Application services are thin use-case orchestrators.
- Mapping, validation, authorization policy, persistence, and external integration stay in dedicated components.
- FastAPI routes do not access repositories or SQLAlchemy.
- Authentication is injected through the Store-owned actor boundary.
- SQLAlchemy session lifecycle is host-owned.
- Persistence mapping, repository construction, and UoW composition are separate responsibilities.
- Package-owned database tables use the `store_` prefix.
- Alembic revision history remains host-owned.
- Cross-package integrations use explicit public contracts rather than persistence coupling.

## Quality and release readiness

The package quality gate is:

```bash
make install-dev
make check
```

`make check` runs:

```text
Ruff lint
Ruff format --check
Pyright strict
pytest
branch coverage >= 85%
```

Individual commands are also available:

```bash
make lint
make format-check
make typecheck
make test
make coverage
```

Before releasing a new package version, run the Store package quality gate and the Identity + Store consumer integration gate. Packaging metadata is defined in `pyproject.toml`; the current package version is `0.1.0` and Python 3.12+ is required.

## Deferred capabilities

The following are intentionally outside the current stable scope: admin moderation HTTP routes, Sellora-specific readiness orchestration, subscription/entitlement enforcement, catalog/channel readiness integrations, multi-store ownership mode, and a broader Business/Organization aggregate.

See `ROADMAP.md` for architectural decisions and the completed extraction stages.
