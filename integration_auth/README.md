# hamresan-integration-auth

Reusable machine-to-machine authentication and authorization primitives for Python applications.

```text
Distribution: hamresan-integration-auth
Import:       integration_auth
Python:       >= 3.12
```

`hamresan-integration-auth` is generic integration infrastructure for internal services, external plugins, partner applications, connectors, workers, agents, and backend-to-backend communication.

It is deliberately separate from `hamresan-identity`:

- `hamresan-identity` owns human users, sessions, and user access tokens;
- `hamresan-integration-auth` owns machine/integration identity, credentials, signed requests, replay protection, permissions, scopes, and credential lifecycle;
- a host application may use both and map them into its own actor abstraction.

The package has no direct dependency on Identity, WordPress, WooCommerce, Store, Subscription, or provider-specific SDKs.

## Current implementation status

Implemented:

- **Stage 1 — Core domain**
  - integration clients, credentials, principals, permissions, scopes, resources, lifecycle and direction;
- **Stage 2 — Signing protocol and crypto contracts**
  - canonical requests and deterministic query canonicalization;
  - SHA-256 body hashing;
  - HMAC-SHA256 signing and constant-time verification;
  - timestamp tolerance policy;
  - fixed known-answer vectors;
- **Stage 3 — Replay protection core**
  - atomic `NonceStore` contract;
  - `ReplayWindowPolicy`;
  - `ReplayProtector` application service;
  - explicit replay and timestamp errors;
  - client-scoped nonce consumption semantics.

Not implemented yet:

- production/persistent nonce storage;
- complete signed-request authentication orchestration;
- authorization services;
- credential issuance/rotation services;
- SQLAlchemy persistence;
- FastAPI adapters/dependencies.

See `ROADMAP.md` for staged delivery.

# Installation

```bash
pip install hamresan-integration-auth
```

For development in this repository:

```bash
cd integration_auth
python -m pip install -e ".[test]"
make check
```

# Core domain

```python
from integration_auth import (
    CredentialDirection,
    CredentialLifecyclePolicy,
    CredentialStatus,
    IntegrationClient,
    IntegrationClientId,
    IntegrationCredential,
    IntegrationCredentialId,
    IntegrationPrincipal,
    IntegrationResource,
    IntegrationScope,
    Permission,
)
```

Machine identity remains independent from human identity. Permission vocabulary is consumer-defined, for example:

```text
catalog.read
catalog.write
orders.read
```

Scopes constrain where permissions apply:

```text
store:store-123
organization:org-42
```

`IntegrationScope` is a grant. `IntegrationResource` is the target of an authorization decision. They intentionally remain separate concepts.

Credential direction is defined from the Python host perspective:

```text
INBOUND  = external integration signs; Python host verifies
OUTBOUND = Python host signs; external integration verifies
```

`IntegrationCredential` does not contain a raw signing secret.

# Signed-request protocol

The initial protocol uses HMAC-SHA256 over this exact canonical representation:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

There is no trailing newline after `BODY_SHA256`.

## Canonical query

```python
from integration_auth.protocol import CanonicalQueryEncoder

canonical_query = CanonicalQueryEncoder().encode(
    [
        ("tag", "sale"),
        ("page", "2"),
        ("tag", "blue sky"),
    ]
)
```

Rules:

1. UTF-8 percent-encoding uses RFC 3986 unreserved characters as safe characters.
2. Space is `%20`, never `+`.
3. Encoded `(key, value)` pairs are sorted lexicographically.
4. Duplicate query keys are preserved.
5. No leading `?` is included.
6. Empty query is an empty string.

## Body hashing and HMAC

```python
from integration_auth.infrastructure.crypto import (
    HmacSha256RequestSigner,
    HmacSha256RequestVerifier,
    Sha256BodyHasher,
)
from integration_auth.protocol import CanonicalRequestSerializer

body_hasher = Sha256BodyHasher()
signer = HmacSha256RequestSigner(CanonicalRequestSerializer())
verifier = HmacSha256RequestVerifier(signer)
```

Verification uses `hmac.compare_digest` for constant-time comparison. Secrets and signatures must never be logged.

Known-answer vector retained by the test suite:

```text
secret:
stage-2-test-secret

body:
{"sku":"SKU-1","stock":5}

body SHA-256:
541dffad76efde94986c635a29f19b29df65fc7d07b44da2576ce9fec007a802

signature:
2c1d0ec86ff34e7d057d2004df2ff4e88745b393938984d956658d748f5f104a
```

# Replay protection

A valid HMAC signature is not enough by itself. Signed requests must also pass timestamp and nonce replay checks.

Public Stage 3 components:

```python
from integration_auth.application.contracts import NonceStore
from integration_auth.application.services import ReplayProtector
from integration_auth.protocol import ReplayWindowPolicy, TimestampTolerancePolicy
```

`NonceStore` defines one critical guarantee:

```text
consume_once(client_id, nonce, expires_at) must be atomic
```

The first consumer of a `(client_id, nonce)` pair receives success. Concurrent or later attempts for the same client/nonce must fail while the nonce remains protected. Production persistence must enforce this at the storage boundary; the application service must not emulate atomicity in memory.

`ReplayProtector`:

1. rejects stale or excessively future timestamps;
2. calculates a safe nonce expiry;
3. calls the atomic nonce store;
4. raises a replay error if the nonce was already consumed.

The replay window is configured explicitly. Even when retention is configured shorter than clock skew, the calculated nonce expiry keeps the nonce until the signed request can no longer be accepted by the timestamp policy.

Stage 3 intentionally does **not** implement SQLAlchemy storage. The persistent atomic implementation belongs to the persistence stage.

# External integrations

A future incoming request may carry headers such as:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
```

The complete request-authentication service that resolves credentials, verifies signatures, invokes replay protection, and builds `IntegrationPrincipal` is a later roadmap stage.

## PHP / WordPress interoperability

WordPress is only an example consumer; it is not a package domain concept.

Once PHP builds the exact same canonical string, standard PHP HMAC is compatible:

```php
$signature = hash_hmac('sha256', $canonicalRequest, $secret);
```

A later interoperability stage will add executable/shared Python-PHP fixtures using the same known-answer vectors.

# Bidirectional communication

The architecture supports both:

```text
External integration -> Python backend
Python backend -> external integration
```

Do not assume the same credential is used in both directions. `CredentialDirection.INBOUND` and `CredentialDirection.OUTBOUND` allow separate lifecycle, rotation and revocation.

# Protecting routes

FastAPI support is not implemented yet.

The target host behavior remains:

```text
invalid or missing integration authentication -> 401 Unauthorized
authenticated integration without permission -> 403 Forbidden
```

Routes must remain thin. They must not rebuild canonical requests, verify HMACs, consume nonces, inspect credential persistence, or implement permission/scope rules directly.

# Credential rotation and persistence

Credential provisioning, rotation and database persistence are later roadmap stages.

When implemented:

- raw secrets must never be stored in plaintext;
- raw secrets should only cross issuance/rotation boundaries when required;
- incoming and outgoing credentials can rotate independently;
- overlap windows must be explicit;
- persistence uses async SQLAlchemy repositories;
- the host owns Engine/SessionMaker;
- the host owns the Alembic revision graph;
- nonce consumption must be atomic under concurrency.

# Integration with hamresan-identity

Do not add a direct package dependency between the two systems.

A host may compose both:

```text
Bearer user token
    -> hamresan-identity
    -> UserActor

Signed machine request
    -> hamresan-integration-auth
    -> IntegrationActor
```

The host may map both into its own `Actor` abstraction. Reusable business modules should depend on that host/domain abstraction rather than on either authentication package directly.

# Architecture

```text
integration_auth/
├── domain/                         # Stage 1
├── protocol/                       # Stage 2 + replay policies
├── application/
│   ├── contracts/
│   │   ├── crypto/                 # Stage 2
│   │   └── replay/                 # Stage 3
│   ├── errors/                     # Stage 3 replay errors
│   └── services/
│       └── replay/                 # Stage 3 ReplayProtector
├── infrastructure/
│   └── crypto/                     # Stage 2
├── migrations/                     # later stage
└── presentation/                   # later stage
```

Tests mirror production responsibility paths. Builders, Factories, Fakes and Test Helpers with independent responsibility belong under `tests/support/...`.

# Quality gates

```bash
make check
```

The package requires:

- Ruff lint;
- Ruff format check;
- Pyright strict;
- pytest;
- branch coverage >= 85%;
- package build.
