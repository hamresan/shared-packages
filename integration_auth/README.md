# hamresan-integration-auth

Reusable machine-to-machine authentication and authorization primitives for Python applications.

```text
Distribution: hamresan-integration-auth
Import:       integration_auth
Python:       >= 3.12
```

The package is generic integration infrastructure for internal services, external plugins,
partner applications, connectors, workers, agents, and backend-to-backend communication.
It has no direct dependency on `hamresan-identity`, WordPress, WooCommerce, Store,
Subscription, or provider-specific SDKs.

`hamresan-identity` authenticates humans. `hamresan-integration-auth` authenticates
machine/integration clients. A host may compose both into its own actor abstraction.

## Current implementation status

Implemented:

- **Stage 1 — Core domain**
  - integration clients, credentials, principals, permissions and scopes;
  - typed client/credential identifiers;
  - inbound/outbound credential direction;
  - active/revoked/expired lifecycle rules.
- **Stage 2 — Signing protocol and crypto contracts**
  - deterministic `CanonicalRequest`;
  - RFC3986 query canonicalization;
  - SHA-256 body hashing;
  - `RequestSigner` / `RequestVerifier` contracts;
  - HMAC-SHA256 signer and constant-time verifier;
  - timestamp-tolerance policy;
  - fixed cross-language known-answer vectors.
- **Stage 3 — Replay protection**
  - atomic `NonceStore` contract;
  - `ReplayWindowPolicy`;
  - `ReplayProtector`;
  - stale/future timestamp rejection;
  - client-scoped nonce consumption and replay errors.
- **Stage 4 — Application authentication**
  - repository/clock/secret-provider contracts;
  - inbound credential eligibility policy;
  - `AuthenticateIntegrationRequestService`;
  - fail-closed authentication and `IntegrationPrincipal` mapping.
- **Stage 5 — Authorization**
  - exact permission requirement policy;
  - exact resource/scope authorization policy;
  - framework-neutral `AuthorizationResult` with stable decision reasons;
  - `IntegrationAuthorizer` for permission-only and permission+resource decisions;
  - `IntegrationAuthorizationError` for require-style enforcement.

Not implemented yet:

- credential issuance/rotation use cases;
- persistent SQLAlchemy repositories and nonce store;
- host-owned Alembic integration;
- FastAPI adapters/dependencies.

See `ROADMAP.md` for staged delivery.

## Installation

```bash
pip install hamresan-integration-auth
```

Development:

```bash
cd integration_auth
python -m pip install -e ".[test]"
make check
```

## Core domain

```python
from integration_auth import (
    CredentialDirection,
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

Authentication answers **who is calling**. Authorization answers **what that integration may
do and on which resource**. Those responsibilities remain separate.

Permission vocabulary is consumer-defined:

```text
catalog.read
catalog.write
orders.read
```

Scopes are generic resource grants:

```text
store:store-123
organization:org-42
```

`IntegrationScope` represents a grant. `IntegrationResource` represents the target of an
authorization decision.

## Signed-request protocol

The initial protocol signs exactly:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

There is no trailing newline.

Canonical query rules:

1. UTF-8 percent-encoding uses RFC3986 unreserved characters.
2. Space is `%20`, never `+`.
3. Encoded `(key, value)` pairs are sorted lexicographically.
4. Duplicate query keys are preserved.
5. The canonical query has no leading `?`.

```python
from integration_auth.protocol import CanonicalQueryEncoder

query = CanonicalQueryEncoder().encode([("tag", "sale"), ("page", "2"), ("tag", "blue sky")])
assert query == "page=2&tag=blue%20sky&tag=sale"
```

Body hashing and HMAC adapters live in infrastructure. Verification uses
`hmac.compare_digest` for constant-time signature comparison. Secrets and signatures must never
be logged.

## Replay protection

Stage 3 requires an atomic nonce-store boundary:

```text
consume_once(client_id, nonce, expires_at_timestamp) -> bool
```

A `(client_id, nonce)` pair may succeed only once while protected. Timestamp validation runs
before nonce consumption. A real database-backed atomic implementation belongs to the
persistence stage.

## Application authentication

Stage 4 composes the signing and replay primitives without depending on SQLAlchemy or FastAPI.

```python
from integration_auth.application import (
    AuthenticateIntegrationRequest,
    AuthenticateIntegrationRequestService,
    IntegrationAuthenticationError,
)
```

The authentication flow is:

```text
resolve client
-> load credential candidates
-> filter usable inbound credentials
-> resolve transient verification material
-> verify signature
-> apply replay protection
-> map IntegrationPrincipal
```

`IntegrationCredential` contains no raw secret. Secret retrieval remains a separate boundary.

## Authorization

Stage 5 authorizes an already authenticated `IntegrationPrincipal` independently of HTTP or
FastAPI.

```python
from integration_auth.application import IntegrationAuthorizer
from integration_auth.domain.policies import (
    PermissionRequirementPolicy,
    ResourceScopeAuthorizationPolicy,
)
from integration_auth import IntegrationResource, Permission

authorizer = IntegrationAuthorizer(
    permission_policy=PermissionRequirementPolicy(),
    resource_scope_policy=ResourceScopeAuthorizationPolicy(),
)

result = authorizer.authorize(
    principal=principal,
    permission=Permission("orders.read"),
    resource=IntegrationResource("store", "store-123"),
)
```

Authorization is fail-closed and exact-match only:

- `orders.read` does not imply `orders.write`;
- `store:store-123` does not imply `store:store-456`;
- matching resource IDs with different resource types do not match;
- wildcard permissions/scopes are not implemented.

Two forms are supported:

```text
route/action-level: permission only
resource-level:     permission + exact resource scope
```

`authorize(...)` returns a framework-neutral decision. `require(...)` raises
`IntegrationAuthorizationError` when access is denied. HTTP mapping remains a presentation-layer
responsibility for Stage 9.

## Bidirectional integrations

Both directions are supported architecturally:

```text
External integration -> Python backend
Python backend -> external integration
```

Credential direction is defined from the Python host perspective:

```text
INBOUND  = external side signs; Python host verifies
OUTBOUND = Python host signs; external side verifies
```

Do not assume the same credential is used in both directions.

## Credential rotation

Provisioning and rotation are not implemented yet. The authentication service already accepts
multiple eligible credential candidates so a future rotation overlap does not require rewriting
authentication orchestration.

Raw secrets must only cross an issuance/rotation boundary when required and must never be stored
in plaintext when persistence is implemented.

## Protecting routes

FastAPI support is not implemented yet. The future adapter should translate HTTP requests into
authentication input, then compose authentication with Stage 5 authorization.

Target behavior:

```text
invalid/missing machine authentication -> 401 Unauthorized
authenticated integration without permission/scope -> 403 Forbidden
```

Business routes must remain thin and must not parse HMAC signatures, consume nonces, inspect
credential storage, or implement authorization rules directly.

## Integration with hamresan-identity

Do not add a package dependency between the two authentication systems. A host may map human and
integration principals into its own application-specific actor abstraction.

## Persistence roadmap

When persistence is introduced:

- use async SQLAlchemy;
- repositories depend on application contracts;
- the host owns Engine/SessionMaker;
- the host owns the Alembic revision graph;
- mapping/hydration stays outside repositories;
- nonce consumption must implement the atomic `NonceStore` contract;
- no FK to Identity/Store/Organization tables;
- secrets are never stored in plaintext.

## Quality gates

```bash
make check
```

Required:

- Ruff lint;
- Ruff format check;
- Pyright strict;
- pytest;
- branch coverage >= 85%;
- package build.
