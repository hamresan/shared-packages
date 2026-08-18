# Identity + Store consumer example

This example is a real host application composition for `hamresan-identity` and `hamresan-store`.

It demonstrates the boundaries expected from consuming services:

- one host-owned async SQLAlchemy engine and sessionmaker;
- Identity and Store sharing that session factory without sharing repositories or models;
- Identity authentication adapted to Store's `AuthenticatedActor` contract in the host composition root;
- Store application services composed with the reusable SQLAlchemy Unit of Work;
- Identity and Store FastAPI adapters installed on the same application;
- host-owned Alembic configuration using both package metadata objects and name filters;
- Docker verification that runs the complete example quality gate without publishing a host port.

## Package boundaries

`hamresan-store` does not import Identity. The host adapter in `identity_store_consumer_app.authentication` depends on Identity's public `AccessTokenAuthenticator`, resolves an `AuthenticatedPrincipal`, and returns Store's `AuthenticatedActor`.

The database is also host-owned. `ConsumerDatabase` creates one engine/sessionmaker and supplies the same `session_factory` to both packages. Identity owns `identity_*` tables and Store owns `store_*` tables.

The example application uses the unique Python package name `identity_store_consumer_app`. This intentionally avoids colliding with other consumer examples when the whole `examples` tree is collected by pytest or analyzed by Pyright.

## Alembic

The root Alembic environment belongs to this consumer, not to either package. `consumer_metadata()` supplies both package metadata objects and `include_consumer_name()` composes their independent filters. Revision identifiers and ordering therefore remain an application concern.

A production consumer would add its revision files under `migrations/versions/` using this host configuration.

## Verification

From this directory, after installing the local packages and this example:

```bash
make check
```

The integration tests verify that one Identity principal can access `/identity/me`, create a Store through `POST /stores`, and read it through `GET /stores/me`. Alembic tests verify autogeneration sees both Identity and Store tables.

Both consumer examples can also be collected together from the repository `examples` directory because `examples/pytest.ini` supplies their source roots without package-name collisions.

Docker verification runs the same checks in a clean Python 3.12 image:

```bash
make docker-test
```

No fixed host port is used; the Docker container exists only to run the verification suite.
