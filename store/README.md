# hamresan-store

Reusable Store domain, application, persistence, and FastAPI adapter package for Python services.

Sellora is used only as a read-only reference during extraction. `hamresan-store` does not import Sellora-specific modules or Identity presentation/implementation code.

## Current scope

Implemented stages include:

- Store aggregate, enums, value objects, and validators.
- Application contracts and Create/Read use cases.
- Async SQLAlchemy persistence with a host-provided session factory.
- FastAPI adapter for create and read operations.
- Host-owned Alembic integration through package metadata/filter helpers.
- Ruff, Pyright strict mode, Pytest, and branch coverage with an 85% minimum gate.

The next roadmap stage is the real consumer integration example.

## SQLAlchemy persistence

The package owns SQLAlchemy models and mapping, but the consuming application owns the engine and session lifecycle.

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from store.infrastructure.persistence.sqlalchemy import (
    build_sqlalchemy_store_unit_of_work_factory,
)

engine = create_async_engine(database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)
store_uow_factory = build_sqlalchemy_store_unit_of_work_factory(session_factory)
```

The package never creates a global engine or sessionmaker. `owner_user_id` is stored as an external UUID reference and has no foreign key to Identity tables.

Package-owned table names use the `store_` prefix. The current Store table is `store_stores`.

## FastAPI adapter

The initial HTTP surface is:

```text
POST /stores
GET  /stores/me
GET  /stores/{store_id}
```

Authentication is supplied by the host application. Store owns only a small actor contract:

```python
from store import AuthenticatedActor
```

The host adapts its authentication system to that contract. For example, a consumer using `hamresan-identity` can adapt the authenticated principal in its own composition root and return `AuthenticatedActor(user_id=principal.user_id)`.

Create-store requests never accept a trusted owner identifier. `owner_user_id` is taken from the authenticated actor and extra request fields are rejected.

Compose the adapter with the application use cases and the host-owned authentication dependency:

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

The Store package does not import `hamresan-identity`; the consumer owns that wiring.

## Alembic integration

Alembic revision history belongs to the consuming application. Install the optional migration dependency when the host uses Alembic:

```bash
pip install "hamresan-store[migrations]"
```

Use the public migration helpers in the host Alembic environment:

```python
from store.migrations import include_store_name, store_metadata

context.configure(
    connection=connection,
    target_metadata=store_metadata(),
    include_name=include_store_name,
    include_schemas=True,
)
```

`store_metadata()` exposes the SQLAlchemy metadata owned by this package. `include_store_name()` limits reflection/autogenerate to `store_*` tables and their child objects. The package intentionally does not ship its own root revision graph or decide migration ordering for the host application.

## Architecture rules

- Domain code has no FastAPI, SQLAlchemy, Identity, or Sellora dependencies.
- Application services remain thin use-case orchestrators.
- FastAPI routes only translate HTTP input/output and invoke presentation endpoint components.
- Request/domain mapping is handled by dedicated presentation mappers.
- Authentication is injected through the Store-owned `AuthenticatedActor` boundary.
- No repository or SQLAlchemy access occurs in presentation routes.
- SQLAlchemy session lifecycle is host-owned through an injected async session factory.
- Persistence mapping, repository construction, and UoW composition are separate responsibilities.
- Package-owned database tables use the `store_` prefix.
- Alembic revision history remains owned by the consuming application.

## Development

```bash
make install-dev
make check
```

`make check` runs Ruff, Ruff format checking, Pyright strict mode, and Pytest with branch coverage.

See `ROADMAP.md` for extraction decisions and the continuation checkpoint.
