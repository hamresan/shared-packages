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
- **Stage 7 — Async SQLAlchemy persistence**
  - host-provided async session factory;
  - client/credential repository adapters;
  - protected-secret persistence and transient recovery;
  - atomic nonce consumption under concurrency;
  - atomic credential rotation transaction;
  - dedicated ORM records and persistence mappers;
  - `integration_auth_` table prefix and authentication-path indexes.
- **Stage 8 — Host-owned Alembic integration**
  - package-owned SQLAlchemy metadata helper;
  - package-owned `include_name` filter;
  - host-owned revision graph and migration environment.
- **Stage 9 — FastAPI adapter**
  - signed-request header parsing and validation;
  - HTTP request to application-authentication mapping;
  - authentication dependency returning `IntegrationPrincipal`;
  - permission/resource-scope dependency factory;
  - generic 401/403 HTTP error mapping;
  - application contracts for injectable authenticator/authorizer implementations;
  - real FastAPI dependency tests.
- **Stage 10 — External protocol interoperability examples**
  - shared deterministic Python/PHP vectors;
  - executable inbound and outbound HMAC-SHA256 examples using separate credentials;
  - executable rotation example;
  - executable exact permission and resource-scope examples;
  - subprocess tests, including real PHP CLI execution when PHP is installed.

Not implemented yet:

- multi-auth host composition example;
- final security/release-hardening stage.

See `ROADMAP.md` for staged delivery.

## Installation

Core package:

```bash
pip install hamresan-integration-auth
```

FastAPI presentation adapter:

```bash
pip install "hamresan-integration-auth[fastapi]"
```

FastAPI remains an optional dependency. Domain, application, protocol, crypto, and persistence
layers do not conceptually depend on FastAPI.

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
logged. Authentication and presentation DTOs exclude signature values from their `repr`.

## Replay protection

Replay protection uses this atomic persistence boundary:

```text
consume_once(client_id, nonce, expires_at_timestamp) -> bool
```

A `(client_id, nonce)` pair may succeed only once while protected. Timestamp validation runs
before nonce consumption. `SqlAlchemyNonceStore` implements the atomic boundary using a database
uniqueness constraint; concurrent replay attempts are covered by persistence integration tests.

## Application authentication

The application layer composes signing and replay primitives without depending on FastAPI.

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

The application also exposes narrow contracts used by presentation adapters:

```python
from integration_auth.application.contracts.authentication import IntegrationRequestAuthenticator
from integration_auth.application.contracts.authorization import IntegrationRequestAuthorizer
```

Concrete application services explicitly implement those contracts.

## Authorization

Authorization operates on an already authenticated principal independently from HTTP.

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

A host provides `CredentialSecretProtector`. Its output is the dedicated
`ProtectedCredentialSecret` type rather than raw secret bytes. Persistence stores only protected
material.

For authentication, the SQLAlchemy secret provider loads protected material and passes it to the
host-provided `CredentialSecretUnprotector`. The recovered secret is transient verification
material and is not added to the domain entity.

Both `IssuedCredential.raw_secret` and `ProtectedCredentialSecret.value` are excluded from their
dataclass `repr`, reducing accidental logging exposure.

### Rotation

Rotation is direction-specific. Incoming and outgoing credentials can be rotated independently.
`RotateCredentialService` takes an explicit `overlap_seconds` value. Existing currently-usable
credentials for the same client and direction are shortened to the overlap deadline; credentials
for the opposite direction are untouched.

The SQLAlchemy provisioning repository implements rotation in one database transaction, so
previous-credential changes and replacement-credential insertion either commit together or roll
back together.

### Revocation and expiration

Credential transitions remain governed by the lifecycle policy:

```text
ACTIVE -> REVOKED
ACTIVE -> EXPIRED
```

`REVOKED` and `EXPIRED` remain terminal states.

## Async SQLAlchemy persistence

Persistence is an infrastructure adapter. The host owns the `AsyncEngine` and
`async_sessionmaker`; the package never creates application-global database infrastructure.

```python
from integration_auth.infrastructure.persistence.sqlalchemy import (
    IntegrationClientRecordMapper,
    IntegrationCredentialRecordMapper,
    SqlAlchemyCredentialSecretProvider,
    SqlAlchemyIntegrationClientRepository,
    SqlAlchemyIntegrationCredentialRepository,
    SqlAlchemyNonceStore,
)
```

The same concrete repositories explicitly implement the application contracts used for
authentication/provisioning. Persistence mapping remains outside application services and domain
entities.

Package tables:

```text
integration_auth_clients
integration_auth_credentials
integration_auth_consumed_nonces
```

There are no foreign keys to Identity, Store, Organization, WordPress, or other host-domain tables.

## Host-owned Alembic integration

The package exposes migration composition helpers but **does not own an Alembic revision chain**.

```python
from integration_auth.migrations import (
    INTEGRATION_AUTH_TABLE_PREFIX,
    include_integration_auth_name,
    integration_auth_metadata,
)
```

For a host whose Alembic environment manages only integration-auth tables:

```python
from alembic import context
from integration_auth.migrations import (
    include_integration_auth_name,
    integration_auth_metadata,
)

context.configure(
    connection=connection,
    target_metadata=integration_auth_metadata(),
    include_name=include_integration_auth_name,
)
```

For a host composing multiple packages, the host may provide multiple metadata objects or combine
package metadata into its own migration composition and compose the package filters according to
its own Alembic setup.

The host owns:

- `alembic.ini`;
- `migrations/env.py`;
- `script.py.mako`;
- revision files and IDs;
- revision ordering and branch heads;
- deployment/rollback policy.

`integration_auth.migrations` owns only the package metadata boundary and the
`integration_auth_` name filter. Real Alembic autogenerate tests verify that the three package
tables are discovered and unrelated host tables are ignored.

## External integration usage

The FastAPI adapter expects these signed-request headers:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
```

The adapter translates FastAPI `Request` data into the existing application authentication input.
It preserves the ASGI raw path when available, preserves duplicate query values through the
canonical query encoder, hashes the request body through `BodyHasher`, and never moves HTTP types
into the application/domain layers.

### Python / PHP interoperability

`examples/interoperability/` contains executable examples backed by one shared `vectors.json`.
The fixture intentionally uses **different inbound and outbound secrets** so consumers do not infer
that a bidirectional integration should reuse one credential.

Run from the package directory:

```bash
python examples/interoperability/python_protocol.py
php examples/interoperability/php_protocol.php
python examples/interoperability/python_lifecycle_authorization.py
```

The Python and PHP protocol examples must produce the same canonical query, body hash, and
HMAC-SHA256 signature byte-for-byte for both directions. The example secrets are deterministic
fixture data only and must never be used in production.

The lifecycle/authorization example also demonstrates:

- rotating only `INBOUND` credentials while `OUTBOUND` credentials remain independent;
- exact permission matching (`orders.read` does not imply `orders.write`);
- exact resource-scope matching (`store:store-123` does not match `store:store-999`).

WordPress is an example PHP consumer, not a package domain concept. A PHP consumer signs the same
canonical request with:

```php
$signature = hash_hmac('sha256', $canonicalRequest, $secret);
```

The output is lowercase hexadecimal and the example verifier uses `hash_equals` when comparing
known signatures.

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

## Protecting FastAPI routes

Compose the adapter in the host application. The package does not create application routes.

```python
from typing import Annotated

from fastapi import Depends, FastAPI, Request

from integration_auth import IntegrationPrincipal, IntegrationResource, Permission
from integration_auth.infrastructure.crypto.hashing import Sha256BodyHasher
from integration_auth.presentation import FastApiIntegrationAuthFactory
from integration_auth.protocol import CanonicalQueryEncoder

integration_http = FastApiIntegrationAuthFactory().create(
    authenticator=authentication_service,
    authorizer=authorizer,
    body_hasher=Sha256BodyHasher(),
    query_encoder=CanonicalQueryEncoder(),
)

app = FastAPI()


@app.get("/integration/profile")
async def integration_profile(
    principal: Annotated[IntegrationPrincipal, Depends(integration_http.authenticate)],
) -> dict[str, str]:
    return {"client_id": principal.client_id.value}
```

For permission + resource-scope enforcement, the host supplies the mapping from its HTTP resource
to the generic `IntegrationResource`:

```python
def store_resource(request: Request) -> IntegrationResource:
    return IntegrationResource("store", str(request.path_params["store_id"]))


require_orders_read = integration_http.permissions.create(
    Permission("orders.read"),
    resource_resolver=store_resource,
)


@app.get("/stores/{store_id}/orders")
async def store_orders(
    principal: Annotated[IntegrationPrincipal, Depends(require_orders_read)],
) -> dict[str, str]:
    return {"client_id": principal.client_id.value}
```

HTTP semantics are fail-closed and intentionally generic:

```text
invalid/missing/malformed machine authentication -> 401 Unauthorized
invalid signature/timestamp/replay               -> 401 Unauthorized
authenticated integration without authorization -> 403 Forbidden
```

Authentication errors do not expose whether the client ID, credential, signature, timestamp, or
nonce was the failing detail. Authorization errors do not expose the missing permission/scope
reason. Routes do not parse signatures, consume nonces, inspect credential storage, decrypt
credentials, or implement authorization rules directly.

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
