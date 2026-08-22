# hamresan-integration-auth

Reusable machine-to-machine authentication and authorization primitives for Python applications.

```text
Distribution: hamresan-integration-auth
Import:       integration_auth
Python:       >= 3.12
```

The package is generic integration infrastructure for internal services, external plugins,
partner applications, connectors, workers, agents, and backend-to-backend communication.
WordPress is only one possible consumer.

It is deliberately separate from `hamresan-identity`:

- `hamresan-identity` authenticates human users and owns user sessions/access tokens;
- `hamresan-integration-auth` authenticates machine clients and owns integration credentials,
  signed requests, replay protection, permissions/scopes, and credential lifecycle;
- a host may compose both into its own actor abstraction without either package depending on the
  other.

The package has no direct dependency on Identity, WordPress, WooCommerce, Store, Organization,
Subscription, or provider-specific SDKs.

## Current implementation status

Implemented:

- **Stage 1 — Core domain**
  - `IntegrationClient`, `IntegrationCredential`, `IntegrationPrincipal`;
  - `Permission`, `IntegrationScope`, `IntegrationResource`;
  - typed client/credential identifiers;
  - inbound/outbound credential direction;
  - active/revoked/expired lifecycle rules.
- **Stage 2 — Signing protocol and crypto contracts**
  - deterministic `CanonicalRequest`;
  - RFC3986 canonical query handling;
  - SHA-256 body hashing;
  - `RequestSigner` / `RequestVerifier` contracts;
  - HMAC-SHA256 signer and constant-time verifier;
  - timestamp-tolerance policy;
  - deterministic interoperability vectors.
- **Stage 3 — Replay protection**
  - atomic `NonceStore` contract;
  - `ReplayWindowPolicy`;
  - `ReplayProtector`;
  - stale/future timestamp rejection;
  - client-scoped nonce consumption.
- **Stage 4 — Application authentication**
  - client/credential repository contracts;
  - transient `CredentialSecretProvider` boundary;
  - `Clock` contract;
  - `AuthenticateIntegrationRequestService`;
  - fail-closed authentication and principal mapping.
- **Stage 5 — Authorization**
  - exact permission policy;
  - exact resource/scope policy;
  - framework-neutral `AuthorizationResult`;
  - `IntegrationAuthorizer`.
- **Stage 6 — Credential lifecycle and provisioning**
  - register integration clients;
  - update permissions/scopes;
  - issue credentials;
  - rotate credentials with an explicit overlap window;
  - revoke and expire credentials;
  - cryptographically strong secret generation;
  - strongly typed protected-secret persistence boundary;
  - raw secret returned only from issuance/rotation results;
  - atomic rotation persistence contract.

Not implemented yet:

- async SQLAlchemy persistence adapters and real atomic nonce/rotation transactions;
- host-owned Alembic integration helpers;
- FastAPI adapters/dependencies;
- executable Python/PHP consumer example.

See `ROADMAP.md` for staged delivery.

## Installation

From a package index when published:

```bash
pip install hamresan-integration-auth
```

Development in this repository:

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

Authentication answers **who is calling**. Authorization answers **what that integration may do
and on which resource**. Those responsibilities remain separate.

Permission vocabulary is host/consumer-defined:

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

## HMAC signed-request protocol

The initial protocol signs exactly:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

There is no trailing newline after `BODY_SHA256`.

Canonical query rules:

1. UTF-8 percent encoding uses RFC3986 unreserved characters.
2. Space is `%20`, never `+`.
3. Encoded `(key, value)` pairs are sorted lexicographically.
4. Duplicate query keys are preserved.
5. The canonical query has no leading `?`.

```python
from integration_auth.protocol import CanonicalQueryEncoder

query = CanonicalQueryEncoder().encode([("tag", "sale"), ("page", "2"), ("tag", "blue sky")])
assert query == "page=2&tag=blue%20sky&tag=sale"
```

Concrete SHA-256/HMAC adapters live in infrastructure. HMAC verification uses
`hmac.compare_digest` for constant-time comparison. Raw secrets and signatures must never be
logged.

## Replay protection

Stage 3 defines this atomic persistence boundary:

```text
consume_once(client_id, nonce, expires_at_timestamp) -> bool
```

A `(client_id, nonce)` pair may succeed only once while protected. Timestamp validation runs
before nonce consumption. The real database-backed atomic implementation belongs to Stage 7.

## Application authentication

Stage 4 composes signing and replay primitives without depending on SQLAlchemy or FastAPI.

```python
from integration_auth.application import (
    AuthenticateIntegrationRequest,
    AuthenticateIntegrationRequestService,
)
```

Authentication flow:

```text
resolve client
-> load credential candidates
-> filter usable inbound credentials
-> resolve transient verification material
-> verify signature
-> apply timestamp/replay protection
-> map IntegrationPrincipal
```

`IntegrationCredential` contains credential metadata only. It never stores raw secret material.

## Authorization

Stage 5 authorizes an already authenticated principal independently from HTTP.

```python
from integration_auth import IntegrationResource, Permission
from integration_auth.application import IntegrationAuthorizer
from integration_auth.domain.policies import (
    PermissionRequirementPolicy,
    ResourceScopeAuthorizationPolicy,
)

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

Authorization is exact-match and fail-closed:

- `orders.read` does not imply `orders.write`;
- `store:store-123` does not match `store:store-456`;
- matching IDs with a different resource type do not match;
- wildcard permissions/scopes are not implemented.

`authorize(...)` returns a framework-neutral result. `require(...)` raises
`IntegrationAuthorizationError` when access is denied. HTTP mapping remains a presentation-layer
responsibility.

## Credential provisioning and lifecycle

Stage 6 adds application use cases without adding database infrastructure.

Public services:

```python
from integration_auth.application import (
    ExpireCredentialService,
    IssueCredentialService,
    RegisterIntegrationClientService,
    RevokeCredentialService,
    RotateCredentialService,
    UpdateIntegrationClientGrantsService,
)
```

Provisioning contracts are explicit:

```python
from integration_auth.application.contracts.provisioning import (
    CredentialSecretGenerator,
    CredentialSecretProtector,
    IntegrationClientIdGenerator,
    IntegrationClientProvisioningRepository,
    IntegrationCredentialIdGenerator,
    IntegrationCredentialProvisioningRepository,
)
```

Standard-library secure generators are available:

```python
from integration_auth.infrastructure.security import (
    SecretsCredentialSecretGenerator,
    UuidIntegrationClientIdGenerator,
    UuidIntegrationCredentialIdGenerator,
)
```

`SecretsCredentialSecretGenerator` produces 32-byte / 256-bit secrets using Python's `secrets`
module.

### Secret protection boundary

The package intentionally does **not** ship a hard-coded encryption implementation or application
key. Key management is a host/infrastructure concern.

A host provides `CredentialSecretProtector`. Its output is not raw `bytes`; it must return the
dedicated type:

```python
from integration_auth.application.security import ProtectedCredentialSecret
```

Credential persistence accepts `ProtectedCredentialSecret`, not the raw secret type. This makes
accidental raw-secret persistence visible to static type checking.

Both `IssuedCredential.raw_secret` and `ProtectedCredentialSecret.value` are excluded from their
dataclass `repr`, reducing accidental logging exposure.

The intended issuance flow is:

```text
generate credential ID
-> generate strong raw secret
-> build ACTIVE credential metadata
-> protect raw secret
-> persist credential + ProtectedCredentialSecret
-> return raw secret once in IssuedCredential
```

The raw secret is returned only from issuance/rotation boundaries. Ordinary credential entities
and later ordinary API responses must not expose it.

### Rotation

Rotation is direction-specific. Incoming and outgoing credentials can be rotated independently.

```text
INBOUND rotation  != OUTBOUND rotation
```

`RotateCredentialService` takes an explicit `overlap_seconds` value. Existing currently-usable
credentials for the same client and direction are shortened to the overlap deadline; credentials
for the opposite direction are untouched.

The provisioning repository exposes one atomic rotation operation:

```text
rotate(
    previous_credentials,
    new_credential,
    protected_secret,
)
```

Stage 6 defines this transaction boundary. Stage 7 must implement it with a real database
transaction so a partial state cannot be persisted.

A zero-second overlap is supported. The domain policy preserves the credential snapshot invariant
that `expires_at` must be later than `issued_at` even when rotation happens in the same timestamp
second.

### Revocation and expiration

Credential transitions remain governed by the Stage 1 lifecycle policy:

```text
ACTIVE -> REVOKED
ACTIVE -> EXPIRED
```

`REVOKED` and `EXPIRED` remain terminal states.

Revocation records `revoked_at`. Expiration records `expires_at`. Lifecycle snapshot construction
is handled by a dedicated domain service rather than hidden inside application-service helper
methods.

### Updating grants

`UpdateIntegrationClientGrantsService` replaces a client's permission and scope sets. It does not
perform authorization itself; Stage 5 remains the authorization decision boundary.

## External integration usage

A future HTTP adapter may receive headers such as:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
```

Header parsing belongs to Stage 9. The core/application layers work with translated application
inputs rather than FastAPI request objects.

### PHP / WordPress interoperability

WordPress is an example consumer, not a package domain concept.

After constructing the exact same canonical request byte-for-byte, PHP can sign with:

```php
$signature = hash_hmac('sha256', $canonicalRequest, $secret);
```

The output must be lowercase hexadecimal. Stage 10 will add executable shared Python/PHP fixtures
rather than relying only on documentation.

## Bidirectional integrations

The architecture supports both directions:

```text
External integration -> Python backend
Python backend -> external integration
```

Credential direction is defined from the Python host perspective:

```text
INBOUND  = external side signs; Python host verifies
OUTBOUND = Python host signs; external side verifies
```

Do not assume one credential is shared in both directions. Each direction can be issued, rotated,
revoked, and expired independently.

## Protecting routes

FastAPI integration is **not implemented yet**. Stage 9 will translate HTTP requests into the
existing authentication/authorization application APIs.

Target semantics:

```text
invalid/missing machine authentication -> 401 Unauthorized
authenticated integration without authorization -> 403 Forbidden
```

Routes must remain thin and must not parse HMAC signatures, consume nonces, inspect credential
storage, decrypt credentials, or implement permission/scope rules directly.

## Persistence roadmap

Stage 7 will add async SQLAlchemy adapters.

Requirements already established by the current contracts:

- host owns `Engine` / `SessionMaker`;
- repositories implement application contracts;
- mappers/hydrators stay separate from repositories;
- raw secrets are never stored in plaintext;
- protected secret material stays behind a dedicated type/boundary;
- nonce consumption is atomic;
- credential rotation is atomic;
- no FK to Identity/Store/Organization tables;
- table names use the `integration_auth_` prefix.

## Integration with hamresan-identity

There is no package dependency between the two authentication systems.

```text
Bearer user token
    -> hamresan-identity
    -> UserActor

Signed machine request
    -> hamresan-integration-auth
    -> IntegrationPrincipal
```

The host may map both into its own application-specific `Actor` abstraction. Reusable business
modules should depend on that host/domain abstraction rather than directly coupling themselves to
either authentication package.

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
