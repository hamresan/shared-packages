# hamresan-identity

Reusable passwordless identity and session package for FastAPI applications using async SQLAlchemy persistence.

Identity owns OTP challenges, passwordless registration/login, session persistence, refresh-token rotation, session revocation, identity normalization, abuse controls, and data-retention cleanup. The host application owns the database engine/session lifecycle, notification infrastructure, access-token integration, deployment topology, scheduling, and production observability.

OTP delivery is delegated through the public `NotificationSender` contract from `hamresan-notification`. Identity does not know about SMS providers, SMTP providers, queues, Redis, workers, reverse proxies, schedulers, or secret managers.

## Features

- Mobile and email identities.
- OTP registration and login.
- OTP resend cooldown, expiry, and atomic attempt limits.
- HMAC-SHA256 storage for OTP codes and refresh tokens.
- Versioned HMAC keys with overlap-based key rotation.
- Secure OTP and refresh-token generation.
- Session creation, refresh-token rotation, reuse detection, family revocation, and revoke-all.
- Access-token issuer/authenticator contracts.
- Optional JWT access-token issuer/authenticator with database-backed session and active-user validation.
- Destination-, requester-, challenge-, and verify-requester rate limiting.
- Trusted request-metadata abstraction for IP/device metadata.
- Async SQLAlchemy persistence with host-provided session factory.
- Public Alembic integration helpers for host-owned migration histories.
- Host-invoked retention cleanup.
- Structured security-event contract.
- FastAPI routes for OTP, sessions, and the current authenticated identity.
- `identity_` table prefix for package-owned tables.
- PostgreSQL concurrency regression coverage for security-sensitive flows.

## Installation

Runtime package:

```bash
pip install hamresan-identity
```

With Alembic migration helpers:

```bash
pip install "hamresan-identity[migrations]"
```

For package development from this repository:

```bash
cd identity
make install-dev
```

## How to use Identity in an application

A host application normally composes five things:

1. an async SQLAlchemy session factory;
2. a `NotificationSender`;
3. an access-token issuer;
4. an access-token authenticator;
5. `IdentityModule` itself.

For production, the host should additionally provide a distributed `RateLimiter`, a real `SecurityEventSink`, and a request-metadata resolver that matches its proxy topology.

### 1. Create the database session factory

Identity does not create an engine or global sessionmaker.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:password@db/app")
session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def identity_session_factory() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session
```

Package-owned tables are:

```text
identity_users
identity_user_identities
identity_otp_challenges
identity_sessions
```

### 2. Provide notification delivery

The recommended composition is to use `hamresan-notification` and pass its public sender into Identity:

```python
notification_sender = notification_module.sender
```

Identity sends OTP notifications with template key `identity.otp` and variables:

```text
otp
purpose
```

Notification rendering, queueing, provider selection, retries, SMS, and email delivery remain outside Identity.

A complete package-composition example is available in:

```text
examples/identity_notification_consumer
```

That example is intentionally development/test oriented and is not a production deployment template.

### 3. Configure access tokens

Applications may provide their own `AccessTokenIssuer` and `AccessTokenAuthenticator`, or use the JWT implementation shipped by Identity.

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

access_token_issuer = JwtAccessTokenIssuer(
    signer=codec,
    clock=clock,
    ttl=timedelta(minutes=15),
)

access_token_authenticator = JwtAccessTokenAuthenticator(
    verifier=codec,
    session_reader=session_reader,
    user_reader=user_reader,
    user_status_policy=UserStatusPolicy(),
    clock=clock,
)
```

For HS256, `jwt_signing_secret` must be at least 32 bytes and should be loaded from the host application's secret-management layer.

JWTs contain the canonical claims required by Identity: user ID (`sub`), session ID (`sid`), issued-at time, and expiration time. Access tokens are not persisted. Authentication validates the JWT and then checks the referenced session and user, so session revocation and non-active user statuses take effect for existing access tokens.

### 4. Compose `IdentityModule`

Minimal composition:

```python
from identity import IdentityModule, IdentityModuleConfig

identity = IdentityModule(
    IdentityModuleConfig(
        session_factory=identity_session_factory,
        notification_sender=notification_sender,
        access_token_issuer=access_token_issuer,
        access_token_authenticator=access_token_authenticator,
        signing_secret=identity_hmac_secret,
    )
)
```

The Identity `signing_secret` is used for HMAC hashing of OTP codes and refresh tokens. It should normally be different from the JWT signing secret.

### 5. Install FastAPI routes

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
POST /identity/sessions/revoke-all
GET  /identity/me
```

`revoke-all` requires an authenticated access token and revokes the user's active session family records through the authenticated user identity.

## Direct Python API

Use cases are also available without FastAPI:

```text
identity.public_api.otp_requester
identity.public_api.otp_verifier
identity.public_api.session_refresher
identity.public_api.session_revoker
identity.public_api.session_bulk_revoker
identity.public_api.data_retention_cleaner
identity.public_api.access_token_authenticator
```

This is useful for workers, CLI tools, internal application orchestration, or hosts that expose Identity through a transport other than FastAPI.

## Configuration

Important `IdentityModuleConfig` defaults:

| Setting | Default | Purpose |
| --- | --- | --- |
| `signing_key_id` | `"v1"` | Current HMAC key identifier |
| `otp_ttl` | 5 minutes | OTP challenge lifetime |
| `otp_resend_delay` | 60 seconds | Cooldown before a new OTP may be sent |
| `otp_max_attempts` | 5 | Maximum failed verification attempts |
| `session_ttl` | 30 days | Refresh-session lifetime |
| `session_absolute_ttl` | 90 days | Absolute refresh-family lifetime |
| `otp_challenge_retention` | 7 days | Cleanup retention for old OTP challenges |
| `session_retention` | 30 days | Cleanup retention for old sessions |
| `retention_cleanup_batch_size` | 500 | Maximum deletes per table per cleanup run |
| `otp_request_burst_limit` | 5 / 15 min | Destination burst limit |
| `otp_request_daily_limit` | 20 / day | Destination daily limit |
| `otp_requester_burst_limit` | 30 / 15 min | Requester/IP OTP-request limit |
| `otp_verify_limit` | 10 / min | Per-challenge verification limit |
| `otp_verify_requester_burst_limit` | 60 / min | Requester/IP verification limit |

All windows are configurable through their corresponding `*_window` settings.

## Rate limiting

Identity exposes a `RateLimiter` contract. If no limiter is supplied, `InMemoryRateLimiter` is used.

The in-memory implementation is suitable for tests, local development, and deliberately single-process deployments. Multi-worker or multi-instance production deployments must inject a shared atomic limiter, typically backed by Redis or an equivalent datastore.

Current semantic scopes cover:

- canonical destination request burst;
- canonical destination daily request volume;
- trusted requester/IP OTP-request burst across destinations;
- per-challenge OTP verification;
- trusted requester/IP OTP-verification burst across challenge IDs.

Destination send quota is consumed only when Identity is actually going to create/send a new OTP. Re-reading the same challenge during resend cooldown does not burn destination send quota, while requester/IP abuse limits still apply.

Production must not silently fall back from a distributed limiter to process-local counters if the distributed backend fails.

Edge throttling at nginx, an API gateway, or a WAF should be used in addition to application-level limits. Edge controls protect against volumetric floods; Identity limits protect semantic authentication flows.

## Trusted request metadata and reverse proxies

Identity does not trust `ip_address` or `device_info` values from JSON request bodies.

The FastAPI adapter derives:

- `device_info` from the observed `User-Agent` header;
- `ip_address` from server-observed request metadata.

`DirectRequestMetadataResolver` is the safe default. It uses the socket peer and ignores `X-Forwarded-For`.

For a controlled reverse-proxy deployment:

```python
from identity.presentation.request_metadata import TrustedProxyRequestMetadataResolver

identity = IdentityModule(
    IdentityModuleConfig(
        ...,
        request_metadata_resolver=TrustedProxyRequestMetadataResolver(
            trusted_proxy_hops=1,
        ),
    )
)
```

Only enable forwarded-header trust when the application is reachable exclusively through known trusted proxies and the exact hop count is known.

For a single nginx hop, overwrite untrusted forwarding state instead of preserving arbitrary client values:

```nginx
location / {
    proxy_pass http://identity_app;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

The application port must not be directly reachable from untrusted networks when forwarded headers are trusted.

IP addresses are validated and canonicalized before they become rate-limit keys, so equivalent IPv4/IPv6 representations use the same requester identity.

## Security events

Identity exposes a `SecurityEventSink` contract. The default sink is a no-op, so production applications that require observability or alerting should inject a real implementation through `IdentityModuleConfig.security_event_sink`.

Security events cover flows such as:

```text
otp.request_rate_limited
otp.verify_rate_limited
otp.attempt_failed
otp.attempts_exceeded
refresh.reuse_detected
session.revoked
session.revoked_all
```

Security-event implementations must not add OTP codes, raw access tokens, raw refresh tokens, HMAC/JWT secrets, or unnecessary destination PII.

Recommended operational alerts are aggregated spikes in failed OTP verification, repeated attempts exhaustion, repeated rate-limit rejection, refresh-token reuse, and unexpected mass session revocation.

## HMAC key rotation

OTP and refresh-token hashes are stored in versioned form:

```text
hmac-sha256$<key-id>$<digest>
```

The current write key is configured with:

```python
IdentityModuleConfig(
    ...,
    signing_secret=current_secret,
    signing_key_id="2026-08",
    previous_signing_secrets={
        "2026-07": previous_secret,
    },
)
```

During normal rotation:

1. deploy a new current secret and a new key ID;
2. keep the previous secret verification-only in `previous_signing_secrets`;
3. maintain overlap long enough for credentials created with the previous key to expire;
4. remove retired keys after the overlap window.

Legacy unversioned hashes are verified against active keys during migration.

For a compromised key, do not preserve it for continuity. Replace it immediately, revoke affected sessions, decide how to handle active OTP challenges, and inspect security events for the exposure window.

Every HMAC secret must be at least 32 bytes. Key IDs must be non-empty and cannot contain `$`.

## Data-retention cleanup

Identity exposes a bounded cleanup use case but intentionally does not own scheduling.

Schedule this from the host application's cron, worker, or scheduler:

```python
await identity.data_retention_cleaner.execute()
```

A daily run is a reasonable baseline for many deployments. Higher-volume systems may run it more frequently.

Cleanup deletes only old eligible records and is bounded by `retention_cleanup_batch_size`. Active OTP challenges and active sessions are not eligible for deletion.

Operations should monitor cleanup failures and ensure the configured cadence prevents unbounded table growth.

## Alembic integration and database migrations

The host application owns the Alembic revision graph. Identity does not ship an independent revision history because a reusable package should not create competing migration heads inside a consuming application.

Identity exposes metadata through:

```python
from identity.migrations import identity_metadata, include_identity_name
```

If the application has its own metadata:

```python
from identity.migrations import identity_metadata
from myapp.database import AppBase

target_metadata = [
    AppBase.metadata,
    identity_metadata(),
]
```

Then use the application's normal workflow:

```bash
alembic revision --autogenerate -m "update identity schema"
alembic upgrade head
```

For Identity-only reflection/autogeneration in a database containing unrelated tables:

```python
from identity.migrations import identity_metadata, include_identity_name

context.configure(
    connection=connection,
    target_metadata=identity_metadata(),
    include_name=include_identity_name,
)
```

`include_identity_name` limits the reflection scope to `identity_` tables and related objects.

Do not use `IdentityBase.metadata.create_all()` as a production upgrade mechanism. Existing production databases must receive reviewed migrations, including required columns and indexes, through the host application's revision graph.

Before deployment, test migrations on a production-like database and verify required Identity indexes exist after upgrade.

## Model and persistence semantics

Canonical security decisions use normalized identity values and canonical session/challenge fields.

Persisted compatibility/audit fields such as raw identity value snapshots and session activity timestamps must not become alternate authoritative security state. In particular:

- identity lookup and uniqueness use normalized identity values;
- OTP lookup uses normalized destination + purpose + recency;
- refresh credentials use HMAC-backed token hashes;
- `last_used_at` represents refresh-token use metadata rather than general access-token activity.

## Production deployment checklist

Before considering a production Identity deployment ready, verify all of the following:

- use a shared/distributed `RateLimiter` when more than one worker/process/instance exists;
- configure nginx/API-gateway/WAF edge throttling for Identity endpoints;
- review trusted-proxy topology and exact hop count;
- prevent untrusted networks from bypassing the trusted proxy;
- inject a real `SecurityEventSink` where audit/alerting is required;
- ensure application/proxy logging does not capture OTPs, raw tokens, secrets, or request bodies for sensitive endpoints;
- schedule and monitor retention cleanup;
- apply reviewed Identity migrations and verify indexes;
- load HMAC and JWT secrets from protected runtime configuration or a secret manager;
- keep HMAC and JWT signing secrets separate where practical;
- rehearse normal HMAC rotation;
- document compromised-key response and session revocation procedures.

## Security status

The August 2026 package-level security remediation and hostile review are complete. Security-sensitive OTP and refresh-session concurrency paths are covered by PostgreSQL integration tests, including atomic OTP consumption/attempt accounting, refresh-token rotation/reuse handling, and refresh-vs-revoke behavior.

The final package quality suite after the hostile review completed with `108 passed` with PostgreSQL integration enabled.

This statement covers package-level controls. Environment-specific security still depends on correct host configuration, especially distributed rate limiting, trusted proxies, security-event routing, retention scheduling, database migrations, and secret management.

## Quality checks

```bash
make test
make coverage
make check
```

`make check` runs Ruff lint, Ruff format checking, Pyright strict type checking, and Pytest with branch coverage. Coverage fails below 85% and writes `coverage.xml`.

PostgreSQL concurrency tests require the integration DSN, for example:

```bash
IDENTITY_TEST_POSTGRES_DSN="postgresql+asyncpg://postgres:postgres@localhost:5452/sellora_test" \
make check
```

## Architecture

```text
FastAPI / public API
        ↓
application use cases
        ↓
contracts / domain
        ↑
SQLAlchemy, security implementations, NotificationSender, host adapters
```

Application services remain focused workflow orchestrators. Persistence stays behind repositories/readers, entity/schema conversion stays in mappers, security behavior stays in dedicated security components and policies, and infrastructure/provider choices remain behind contracts and dependency injection.
