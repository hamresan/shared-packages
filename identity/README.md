# hamresan-identity

Reusable identity foundation for FastAPI applications using SQLAlchemy async persistence.

## Current status

This package is not yet feature-complete. The current branch provides the reusable identity foundation:

- identity user, identifier, OTP challenge, and session persistence models;
- `identity_` table naming prefix;
- host-owned async SQLAlchemy session factory contract;
- SQLAlchemy unit-of-work transaction boundary;
- public access-token authentication contract and authenticated principal;
- FastAPI authentication adapter with `/identity/me`;
- strict Ruff, Pyright, Pytest, and coverage checks.

OTP request/verification services, registration/login orchestration, session issuance/refresh/revocation, and integration with `hamresan-notification` are the next implementation stage and are not documented here as completed features.

## Database ownership

The package does not create an SQLAlchemy engine or sessionmaker. The consuming application owns database configuration and lifecycle and injects an `AsyncSessionFactory`.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from identity import IdentityModule, IdentityModuleConfig

engine = create_async_engine("postgresql+asyncpg://...")
session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def identity_session_factory() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session
```

The host also supplies an implementation of the public `AccessTokenAuthenticator` contract:

```python
from identity.public import AccessTokenAuthenticator, AuthenticatedPrincipal


class ApplicationAccessTokenAuthenticator(AccessTokenAuthenticator):
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal: ...
```

Then compose the module:

```python
identity = IdentityModule(
    IdentityModuleConfig(
        session_factory=identity_session_factory,
        access_token_authenticator=ApplicationAccessTokenAuthenticator(),
    )
)
```

## FastAPI integration

Install the router into an existing FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI()
identity.fastapi.install(app)
```

The current adapter exposes:

```text
GET /identity/me
```

with a Bearer access token. A successful response contains the authenticated `user_id` and `session_id`.

## SQLAlchemy metadata

For migrations or metadata inspection, import the persistence package API so all identity models are registered:

```python
from identity.infrastructure.persistence.sqlalchemy import IdentityBase

metadata = IdentityBase.metadata
```

Current tables are:

```text
identity_users
identity_user_identities
identity_otp_challenges
identity_sessions
```

## Development

Create and activate a virtual environment, then install development dependencies:

```bash
make install-dev
```

Run all quality checks:

```bash
make check
```

The test command collects branch coverage for the `identity` source package, prints missing lines, writes `coverage.xml`, and fails when total coverage is below 85%.

Individual checks can also be run with:

```bash
make lint
make format-check
make typecheck
make test
```

## Architecture rule

The host owns infrastructure lifecycle. Identity owns identity behavior and persistence mappings but receives replaceable dependencies through contracts. Future OTP delivery will depend on the public `NotificationSender` API from `hamresan-notification`; Identity will not know about SMS providers, SMTP, Redis, workers, or notification templates.
