# hamresan-identity

Reusable passwordless identity and session package for FastAPI applications using async SQLAlchemy persistence.

Identity owns OTP challenges, passwordless registration/login, session persistence, refresh-token rotation, and revocation. The host application owns the database engine/session lifecycle and the access-token representation.

OTP delivery is delegated through the public `NotificationSender` contract from `hamresan-notification`. Identity does not know about SMS providers, SMTP, queues, Redis, workers, or notification provider details.

## Features

- Mobile and email identities.
- OTP registration and login.
- OTP resend cooldown, expiry, and attempt limits.
- HMAC-SHA256 storage for OTP codes and refresh tokens.
- Secure OTP and refresh-token generation.
- Session creation, refresh-token rotation, and revocation.
- Host-provided access-token issuer and authenticator contracts.
- Async SQLAlchemy persistence with host-provided session factory.
- FastAPI routes for OTP, sessions, and the current authenticated identity.
- `identity_` table prefix for package-owned tables.
- Ruff, Pyright strict mode, Pytest, and branch coverage with an 85% minimum.

## Development installation

From the `identity` directory:

```bash
make install-dev
```

This installs `../notification` first, then installs Identity and its test dependencies.

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

For migrations, use the package metadata:

```python
from identity.infrastructure.persistence.sqlalchemy import IdentityBase

metadata = IdentityBase.metadata
```

Current tables:

```text
identity_users
identity_user_identities
identity_otp_challenges
identity_sessions
```

## Notification integration

Compose `hamresan-notification` in the host application and pass its public sender into Identity:

```python
notification_sender = notification_module.sender
```

Identity sends OTP messages with template key `identity.otp` and variables `otp` and `purpose`. Notification remains responsible for template rendering, provider selection, queueing, and delivery.

## Access-token contracts

The host application supplies implementations of these public contracts:

```python
from identity import AccessTokenAuthenticator, AccessTokenIssuer
```

`AccessTokenIssuer` creates the access token for a user/session pair. `AccessTokenAuthenticator` validates an incoming access token and returns an `AuthenticatedPrincipal`.

This allows Identity to manage sessions without being coupled to a particular token library or provider.

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

The signing secret is used only by the package HMAC hasher for OTP and refresh-token hashes. Supply it from the host configuration layer.

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

### Request an OTP

```json
{
  "identity_type": "mobile",
  "destination": "+96890000000",
  "purpose": "registration",
  "locale": "en"
}
```

For login, use `"purpose": "login"`. Registration is rejected for an existing identity and login is rejected for an unknown identity.

### Verify an OTP

```json
{
  "challenge_id": "<uuid>",
  "code": "123456",
  "full_name": "Mehran",
  "device_info": "web",
  "ip_address": "127.0.0.1"
}
```

`full_name` is required for registration. Successful verification creates a session and returns access-token and refresh-token data.

### Refresh a session

```json
{
  "refresh_token": "<refresh-token>",
  "device_info": "web"
}
```

Refresh tokens are rotated. The previous session is revoked and linked to its replacement.

### Revoke a session

```json
{
  "refresh_token": "<refresh-token>"
}
```

Successful revocation returns HTTP `204`.

## Direct Python API

The use cases are also available through `identity.public_api` without FastAPI:

```python
from identity import RequestOtpCommand
from identity.domain import IdentityType, OtpPurpose

result = await identity.public_api.otp_requester.execute(
    RequestOtpCommand(
        identity_type=IdentityType.MOBILE,
        destination="+96890000000",
        purpose=OtpPurpose.LOGIN,
    )
)
```

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
SQLAlchemy, security implementations, NotificationSender
```

Application services orchestrate workflows only. Persistence stays in repositories, entity/schema conversion stays in mappers, security behavior stays in dedicated security components, entity construction stays in factories, and OTP eligibility rules stay in policies.
