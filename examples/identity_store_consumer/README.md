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

Authentication failures are mapped narrowly: only Identity's public `AccessTokenAuthenticationError` becomes HTTP 401. Unexpected infrastructure or backend failures are allowed to propagate so they are not incorrectly reported as invalid user credentials.

The database is also host-owned. `ConsumerDatabase` creates one engine/sessionmaker and supplies the same `session_factory` to both packages. Identity owns `identity_*` tables and Store owns `store_*` tables.

The example application uses the unique Python package name `identity_store_consumer_app`. This intentionally avoids colliding with other consumer examples when the whole `examples` tree is collected by pytest or analyzed by Pyright.

## Example-only authentication and secrets

`InMemoryAccessTokenAdapter` exists only to make the example self-contained. It demonstrates the `AccessTokenIssuer` and `AccessTokenAuthenticator` boundaries, but it is not a production token implementation and should not be copied into a deployed application.

The Identity signing secret is loaded from the `IDENTITY_SIGNING_SECRET` environment variable. When the variable is not present, the example falls back to an explicitly example-only development secret so local verification remains simple. A production consumer must provide the secret through its real secret-management/runtime configuration and must not rely on the fallback value.

Example:

```bash
export IDENTITY_SIGNING_SECRET='replace-with-a-real-runtime-secret'
```

Production hosts should also provide their production rate limiter, trusted request-metadata resolver, security-event sink, cleanup scheduling, and other deployment controls described by the Identity package README.

## Alembic

The root Alembic environment belongs to this consumer, not to either package. `consumer_metadata()` supplies both package metadata objects and `include_consumer_name()` composes their independent filters. Revision identifiers and ordering therefore remain an application concern.

A production consumer would add its revision files under `migrations/versions/` using this host configuration.

## Verification

From this directory, after installing the local packages and this example:

```bash
make check
```

The integration tests verify that one Identity principal can access `/identity/me`, create a Store through `POST /stores`, and read it through `GET /stores/me`. Authentication boundary tests verify that unexpected authenticator failures are not collapsed into HTTP 401. Alembic tests verify autogeneration sees both Identity and Store tables.

Both consumer examples can also be collected together from the repository `examples` directory because `examples/pytest.ini` supplies their source roots without package-name collisions.

Docker verification runs the same checks in a clean Python 3.12 image:

```bash
make docker-test
```

No fixed host port is used; the Docker container exists only to run the verification suite.
