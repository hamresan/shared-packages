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
- `hamresan-integration-auth` owns machine/integration identity, credentials, signed requests, permissions, scopes, and credential lifecycle;
- a host application may use both and map them into its own actor abstraction.

The package has no direct dependency on Identity, WordPress, WooCommerce, Store, Subscription, or provider-specific SDKs.

## Current implementation status

Implemented:

- **Stage 1 — Core domain**
  - `IntegrationClient`;
  - `IntegrationCredential` metadata without raw secret material;
  - `IntegrationPrincipal`;
  - typed client/credential identifiers;
  - `Permission`, `IntegrationScope`, `IntegrationResource`;
  - inbound/outbound credential direction;
  - active/revoked/expired lifecycle and transition policy.
- **Stage 2 — Signing protocol and cryptographic contracts**
  - `CanonicalRequest`;
  - deterministic canonical query encoding;
  - exact canonical request serialization;
  - `BodyHasher`, `RequestSigner`, and `RequestVerifier` contracts;
  - SHA-256 body hashing;
  - HMAC-SHA256 request signing;
  - constant-time HMAC verification;
  - configurable timestamp-tolerance policy;
  - fixed known-answer vectors suitable for cross-language interoperability tests.

Not implemented yet:

- nonce/replay persistence and atomic nonce consumption;
- request-authentication application services;
- authorization services;
- credential issuance/rotation services;
- SQLAlchemy persistence;
- FastAPI adapters/dependencies.

See `ROADMAP.md` for staged delivery.

# Installation

From a package index when published:

```bash
pip install hamresan-integration-auth
```

For development in this repository:

```bash
cd integration_auth
python -m pip install -e ".[test]"
make check
```

# Stage 1 domain API

The package distinguishes machine identity from human identity.

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

Example client grants:

```python
client = IntegrationClient(
    client_id=IntegrationClientId("wp_store_123"),
    permissions=frozenset(
        {
            Permission("catalog.read"),
            Permission("catalog.write"),
            Permission("orders.read"),
        }
    ),
    scopes=frozenset({IntegrationScope("store", "store-123")}),
)
```

Credential direction is defined from the Python host application's perspective:

```text
INBOUND  = external integration signs; Python host verifies
OUTBOUND = Python host signs; external integration verifies
```

A credential does not contain a raw signing secret:

```python
credential = IntegrationCredential(
    credential_id=IntegrationCredentialId("credential-1"),
    client_id=IntegrationClientId("wp_store_123"),
    direction=CredentialDirection.INBOUND,
    status=CredentialStatus.ACTIVE,
    issued_at=issued_at,
)
```

The Stage 1 lifecycle allows:

```text
ACTIVE -> REVOKED
ACTIVE -> EXPIRED
```

`REVOKED` and `EXPIRED` are terminal states at this stage.

# Stage 2 signed-request protocol

The initial protocol uses HMAC-SHA256 over one exact canonical request representation.

The signed fields are exactly:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

There is **no trailing newline** after `BODY_SHA256`.

## Canonical query rules

Use `CanonicalQueryEncoder` to construct the query portion.

```python
from integration_auth.protocol import CanonicalQueryEncoder

canonical_query = CanonicalQueryEncoder().encode(
    [
        ("tag", "sale"),
        ("page", "2"),
        ("tag", "blue sky"),
    ]
)

assert canonical_query == "page=2&tag=blue%20sky&tag=sale"
```

Rules:

1. Keys and values are UTF-8 percent-encoded using RFC 3986 unreserved characters as safe characters: `A-Z a-z 0-9 - . _ ~`.
2. Space is encoded as `%20`, never `+`.
3. Encoded `(key, value)` pairs are sorted lexicographically by encoded key and then encoded value.
4. Duplicate query keys are preserved.
5. The canonical query string does not include a leading `?`.
6. An empty query is represented by an empty string.

The request path is supplied separately as an origin-form path such as `/api/catalog/products`. It must not contain a query string or fragment. Stage 2 does not silently normalize or rewrite the path.

## Body hash

```python
from integration_auth.infrastructure.crypto import Sha256BodyHasher

body = b'{"sku":"SKU-1","stock":5}'
body_hash = Sha256BodyHasher().hash(body)
```

The result is lowercase 64-character SHA-256 hexadecimal text.

## Canonical request

```python
from integration_auth.protocol import CanonicalRequest, CanonicalRequestSerializer

request = CanonicalRequest(
    method="POST",
    path="/api/catalog/products",
    canonical_query="page=2&tag=blue%20sky&tag=sale",
    timestamp=1787390042,
    nonce="7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3",
    body_sha256=body_hash,
)

canonical_text = CanonicalRequestSerializer().serialize(request)
```

`method` must already be uppercase. The protocol fails closed on invalid canonical values instead of silently normalizing them.

For the example above, the canonical request is:

```text
POST
/api/catalog/products?page=2&tag=blue%20sky&tag=sale
1787390042
7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
541dffad76efde94986c635a29f19b29df65fc7d07b44da2576ce9fec007a802
```

## Crypto contracts

Application code depends on explicit contracts rather than HMAC implementations:

```python
from integration_auth.application.contracts.crypto import (
    BodyHasher,
    RequestSigner,
    RequestVerifier,
)
```

Concrete HMAC/SHA-256 adapters live in infrastructure:

```python
from integration_auth.infrastructure.crypto import (
    HmacSha256RequestSigner,
    HmacSha256RequestVerifier,
    Sha256BodyHasher,
)
from integration_auth.protocol import CanonicalRequestSerializer

signer = HmacSha256RequestSigner(CanonicalRequestSerializer())
verifier = HmacSha256RequestVerifier(signer)
```

Implementations explicitly implement their contracts. Application services added in later stages should depend on `RequestSigner` / `RequestVerifier`, not on the HMAC classes.

## Signing

```python
signature = signer.sign(request, secret)
```

The Stage 2 HMAC signature is lowercase hexadecimal HMAC-SHA256.

Known-answer vector:

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

This vector is stored under `tests/support/protocol` so later PHP/WordPress interoperability tests can reuse exactly the same values.

## Verification

```python
is_valid = verifier.verify(request, secret, signature)
```

HMAC verification uses `hmac.compare_digest` for constant-time signature comparison.

Changing any signed value changes verification, including:

- path;
- canonical query;
- timestamp;
- nonce;
- body hash;
- signature.

Secrets and signatures must not be logged.

# Timestamp tolerance and replay protection

Stage 2 includes only the configurable clock-skew policy:

```python
from integration_auth.protocol import TimestampTolerancePolicy

policy = TimestampTolerancePolicy(max_clock_skew_seconds=300)
allowed = policy.allows(
    request_timestamp=1787390042,
    current_timestamp=1787390100,
)
```

The policy accepts timestamps at both positive and negative skew boundaries and rejects values outside the configured tolerance.

**Nonce consumption and replay prevention are Stage 3 concerns and are not implemented yet.** A signed request must not be considered fully authenticated merely because its HMAC signature verifies.

# External integration usage

A future incoming request may carry headers such as:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
```

Header parsing and request authentication orchestration belong to later application/presentation stages. Stage 2 provides the protocol and crypto building blocks only.

## PHP / WordPress interoperability

WordPress is an example consumer, not a package domain concept.

Once PHP has built the exact canonical string using the same query rules, signing is compatible with PHP's standard HMAC function:

```php
$signature = hash_hmac('sha256', $canonicalRequest, $secret);
```

The output must be lowercase hexadecimal and the canonical request must match the Stage 2 representation byte-for-byte.

A later interoperability stage will add executable/shared Python-PHP vectors rather than relying only on documentation snippets.

# Bidirectional integrations

The architecture supports both directions:

```text
External integration -> Python backend
Python backend -> external integration
```

Do not assume the same credential is used in both directions.

Use Stage 1 credential direction to model separate credentials:

```text
INBOUND
    external side signs
    Python host verifies

OUTBOUND
    Python host signs
    external side verifies
```

Each credential can later be revoked or rotated independently.

# Permissions and resource scopes

Authentication answers:

```text
Who is calling?
```

Authorization answers:

```text
What may this integration do?
On which resource may it do it?
```

Permission vocabulary is consumer-defined:

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

`IntegrationScope` represents a grant. `IntegrationResource` represents the target resource of an authorization decision. They intentionally remain separate concepts.

Authorization services are implemented in a later roadmap stage.

# Protecting FastAPI routes

FastAPI integration is **not implemented yet**. The eventual adapter should authenticate the signed request and then enforce permission/resource authorization without duplicating security logic in route handlers.

Target behavior:

```text
invalid or missing integration authentication -> 401 Unauthorized
authenticated integration without permission -> 403 Forbidden
```

Business routes must remain thin and must not parse HMAC signatures, inspect credential persistence, or implement resource-scope rules directly.

# Credential rotation and persistence

Credential provisioning, rotation, revocation use cases, and persistence are later stages.

When implemented:

- secrets must never be stored in plaintext;
- raw secrets should only cross the issuance/rotation boundary when required;
- incoming and outgoing credentials can rotate independently;
- overlap windows must be explicit;
- persistence uses async SQLAlchemy repositories;
- the host application owns Engine/SessionMaker;
- the host owns the Alembic revision graph;
- nonce consumption must eventually be atomic.

# Integration with hamresan-identity

Do not introduce a package dependency between the two authentication systems.

A host may compose both:

```text
Bearer user token
    -> hamresan-identity
    -> UserActor

Signed machine request
    -> hamresan-integration-auth
    -> IntegrationActor
```

The host may then map both into its own application-specific `Actor` abstraction. Reusable business modules should depend on the host/domain actor contract rather than directly coupling themselves to either authentication package.

# Architecture

```text
integration_auth/
├── domain/                         # Stage 1
│   ├── entities/
│   ├── enums/
│   ├── policies/
│   ├── validators/
│   └── value_objects/
├── protocol/                       # Stage 2
│   ├── canonicalization/
│   ├── policies/
│   ├── validators/
│   └── value_objects/
├── application/
│   └── contracts/
│       └── crypto/                 # Stage 2 contracts
├── infrastructure/
│   └── crypto/
│       ├── hashing/                # Stage 2 SHA-256
│       └── hmac/                   # Stage 2 HMAC-SHA256
├── migrations/                     # later stage
└── presentation/                   # later stage
```

Tests mirror production responsibility paths. Reusable Builders, Factories, Fakes, and Test Helpers belong under `tests/support/...` rather than inside test functions/files.

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
