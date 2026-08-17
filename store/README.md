# hamresan-store

Reusable Store domain, application, persistence, and FastAPI adapter package for Python services.

Sellora is used only as a read-only reference during extraction. `hamresan-store` does not import Sellora-specific modules or Identity presentation/implementation code.

## Current scope

Implemented stages include:

- Store aggregate, enums, value objects, and validators.
- Application contracts and Create/Read use cases.
- Async SQLAlchemy persistence with a host-provided session factory.
- FastAPI adapter for create and read operations.
- Ruff, Pyright strict mode, Pytest, and branch coverage with an 85% minimum gate.

The next roadmap stage is host-owned Alembic integration.

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

## Architecture rules

- Domain code has no FastAPI, SQLAlchemy, Identity, or Sellora dependencies.
- Application services remain thin use-case orchestrators.
- FastAPI routes only translate HTTP input/output and invoke presentation endpoint components.
- Request/domain mapping is handled by dedicated presentation mappers.
- Authentication is injected through the Store-owned `AuthenticatedActor` boundary.
- No repository or SQLAlchemy access occurs in presentation routes.
- SQLAlchemy session lifecycle is host-owned through an injected async session factory.
- Package-owned database tables use the `store_` prefix.
- Alembic revision history remains owned by the consuming application.

## Development

```bash
make install-dev
make check
```

`make check` runs Ruff, Ruff format checking, Pyright strict mode, and Pytest with branch coverage.

See `ROADMAP.md` for extraction decisions and the continuation checkpoint.
