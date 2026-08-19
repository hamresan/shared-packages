# hamresan-identity

Reusable passwordless identity and session package for FastAPI applications using async SQLAlchemy persistence.

Identity owns OTP challenges, passwordless registration/login, session persistence, refresh-token rotation, and revocation. The host application owns the database engine/session lifecycle. The package exposes access-token contracts and also provides an optional production JWT implementation.

OTP delivery is delegated through the public `NotificationSender` contract from `hamresan-notification`. Identity does not know about SMS providers, SMTP, queues, Redis, workers, or notification provider details.

## Features

- Mobile and email identities.
- OTP registration and login.
- OTP resend cooldown, expiry, and attempt limits.
- HMAC-SHA256 storage for OTP codes and refresh tokens.
- Secure OTP and refresh-token generation.
- Session creation, refresh-token rotation, and revocation.
- Access-token issuer and authenticator contracts.
- Production JWT access-token issuer/authenticator with database-backed session and active-user validation.
- Async SQLAlchemy persistence with host-provided session factory.
- Public Alembic integration helpers for host-owned migration histories.
- FastAPI routes for OTP, sessions, and the current authenticated identity.
- `identity_` table prefix for package-owned tables.
- Ruff, Pyright strict mode, Pytest, and branch coverage with an 85% minimum.

## Development installation

From the `identity` directory:

```bash
make install-dev
```

This installs `../notification`, Identity test dependencies, and the optional Alembic migration tooling.

For an application that only needs runtime Identity features:

```bash
pip install hamresan-identity
```

For an application that also manages Identity schema changes with Alembic:

```bash
pip install "hamresan-identity[migrations]"
```

## Database ownership

The package does not create a SQLAlchemy engine or global sessionmaker. The host injects an async session context-manager factory.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine("postgresql+asyncpg://...")
session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def identity_session_factory() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session
```

Current package-owned tables:

```text
identity_users
identity_user_identities
identity_otp_challenges
identity_sessions
```

## Alembic integration

The host application owns the Alembic revision graph. Identity does not ship an independent revision history because package-owned revisions with their own heads can conflict with an application's existing migration graph.

Identity instead exposes its SQLAlchemy metadata and an optional reflection filter through the public `identity.migrations` API:

```python
from identity.migrations import identity_metadata, include_identity_name
```

### Combined application migrations

If the application already has its own SQLAlchemy metadata, configure Alembic with both metadata collections:

```python
from identity.migrations import identity_metadata
from myapp.database import AppBase

target_metadata = [
    AppBase.metadata,
    identity_metadata(),
]
```

Use that value in the host application's Alembic `env.py`:

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
)
```

The application's normal migration workflow can then create the Identity schema inside the same revision graph:

```bash
alembic revision --autogenerate -m "add identity tables"
alembic upgrade head
```

### Identity-only autogeneration

If a migration run should inspect only Identity-owned tables in a database that also contains unrelated application tables, use the provided name filter:

```python
from identity.migrations import identity_metadata, include_identity_name

context.configure(
    connection=connection,
    target_metadata=identity_metadata(),
    include_name=include_identity_name,
)
```

`include_identity_name` accepts only tables beginning with `identity_` and objects belonging to those tables. This prevents an Identity-only autogenerate run from treating unrelated application tables as candidates for removal.

Do not call `IdentityBase.metadata.create_all()` as the production schema-management strategy. It is useful for isolated tests, but production applications should evolve the schema through their normal Alembic revision history.

## Notification integration

Compose `hamresan-notification` in the host application and pass its public sender into Identity:

```python
notification_sender = notification_module.sender
```

Identity sends OTP messages with template key `identity.otp` and variables `otp` and `purpose`. Notification remains responsible for template rendering, provider selection, queueing, and delivery.

## Production JWT access tokens

The package ships an optional JWT implementation exposed from `identity.access_tokens`.

```python
from datetime import timedelta

from identity.access_tokens import (
    JwtAccessTokenAuthenticator,
    JwtAccessTokenIssuer,
    PyJwtHmacCodec,
    SqlAlchemySessionReader,
    SqlAlchemyUserReader,
    UserStatusPolicy,
)
from identity.infrastructure.security.system_clock import SystemClock

clock = SystemClock()
codec = PyJwtHmacCodec(secret=jwt_signing_secret)
session_reader = SqlAlchemySessionReader(identity_session_factory)
user_reader = SqlAlchemyUserReader(identity_session_factory)
user_status_policy = UserStatusPolicy()

access_token_issuer = JwtAccessTokenIssuer(
    signer=codec,
    clock=clock,
    ttl=timedelta(minutes=15),
)

access_token_authenticator = JwtAccessTokenAuthenticator(
    verifier=codec,
    session_reader=session_reader,
    user_reader=user_reader,
    user_status_policy=user_status_policy,
    clock=clock,
)
```

For the default HS256 algorithm, `jwt_signing_secret` must be at least 32 bytes long. `PyJwtHmacCodec` rejects shorter secrets during construction. Generate the secret from a cryptographically secure source and load it from the host application's secret/configuration layer; do not hard-code it in application code or commit it to the repository.

The JWT contains only the canonical token claims needed by Identity: user ID (`sub`), session ID (`sid`), issued-at time, and expiration time. Access tokens are not stored in the database.

Authentication verifies the JWT signature and structure first, then reads the referenced session through the `SessionReader` contract and the referenced user through the `UserReader` contract. The token is rejected if it is expired, if the session is missing, revoked, expired, or belongs to another user, or if the user is missing or is not `ACTIVE`. This makes `PENDING`, `SUSPENDED`, and `DISABLED` status changes effective for existing access tokens without embedding mutable account state into the JWT.

The concrete SQLAlchemy readers are isolated behind `SessionReader` and `UserReader`, so the authenticator itself does not depend on SQLAlchemy.

Refresh tokens remain hash-backed session credentials in the database and continue to use the existing rotation/revocation flow.

Hosts can still provide their own `AccessTokenIssuer` and `AccessTokenAuthenticator` implementations instead of JWT.

## Compose Identity

```python
from identity import IdentityModule, IdentityModuleConfig

identity = IdentityModule(
    IdentityModuleConfig(
        session_factory=identity_session_factory,
        notification_sender=notification_sender,
        access_token_issuer=access_token_issuer,
        access_token_authenticator=access_token_authenticator,
        signing_secret=identity_signing_secret,
    )
)
```

Default settings are 5 minutes for OTP lifetime, 60 seconds for resend delay, 5 maximum OTP attempts, and 30 days for refresh sessions. They can be overridden through `IdentityModuleConfig`.

The signing secret in `IdentityModuleConfig` is used by the package HMAC hasher for OTP and refresh-token hashes. JWT signing can use a separate secret supplied to `PyJwtHmacCodec`.

## FastAPI integration

```python
from fastapi import FastAPI

app = FastAPI()
identity.fastapi.install(app)
```

Routes:

```text
POST /identity/otp/request
POST /identity/otp/verify
POST /identity/sessions/refresh
POST /identity/sessions/revoke
GET  /identity/me
```

## Direct Python API

The use cases are also available through `identity.public_api` without FastAPI.

Public services:

```text
identity.public_api.otp_requester
identity.public_api.otp_verifier
identity.public_api.session_refresher
identity.public_api.session_revoker
identity.public_api.access_token_authenticator
```

## Quality checks

```bash
make test
make coverage
make check
```

`make check` runs Ruff lint, Ruff format check, Pyright strict type checking, and Pytest with branch coverage. Coverage fails below 85% and writes `coverage.xml`.

## Architecture

```text
FastAPI / public API
        ↓
application use cases
        ↓
contracts / domain
        ↑
SQLAlchemy, JWT/security implementations, NotificationSender
```

Application services orchestrate workflows only. Persistence stays in repositories/readers, entity/schema conversion stays in mappers, security behavior stays in dedicated security components and policies, entity construction stays in factories, and OTP eligibility rules stay in policies.
