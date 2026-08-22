# hamresan-integration-auth

Reusable machine-to-machine authentication and authorization for Python applications.

```text
Distribution: hamresan-integration-auth
Import:       integration_auth
Python:       >= 3.12
```

`hamresan-integration-auth` is generic integration infrastructure for internal services, external
plugins, partner applications, connectors, workers, agents, and backend-to-backend communication.
WordPress is only one possible consumer.

It is deliberately separate from `hamresan-identity`:

- `hamresan-identity` authenticates human users and owns user sessions/access tokens;
- `hamresan-integration-auth` authenticates machine clients and owns integration credentials,
  signed requests, replay protection, permissions/scopes, and credential lifecycle;
- a host may compose both into its own actor abstraction without either package depending on the
  other.

The package has no direct dependency on Identity, WordPress, WooCommerce, Store, Organization,
Subscription, or provider-specific SDKs.

## What is implemented

The roadmap is complete through Stage 12. The package currently includes:

- integration clients, credentials, principals, permissions, scopes, and resources;
- HMAC-SHA256 request signing and constant-time verification;
- deterministic canonical requests and RFC3986 query canonicalization;
- clock-skew validation and atomic replay protection;
- application authentication and authorization services;
- credential registration, issuance, rotation, revocation, expiration, and grant updates;
- async SQLAlchemy persistence with host-owned sessions;
- host-owned Alembic composition helpers;
- FastAPI authentication/authorization dependencies;
- Python/PHP interoperability examples;
- host-level multi-auth composition example with `hamresan-identity`;
- security/release hardening, wheel smoke checks, and deployment checklist.

See `ROADMAP.md` for implementation history and `SECURITY_REVIEW.md` for release/deployment
security requirements.

## Installation

Core package:

```bash
pip install hamresan-integration-auth
```

With the FastAPI presentation adapter:

```bash
pip install "hamresan-integration-auth[fastapi]"
```

FastAPI is optional. Domain, application, protocol, crypto, and persistence layers do not depend on
FastAPI conceptually.

Development in this repository:

```bash
cd integration_auth
python -m pip install -e ".[test]"
make check
make release-check
```

## Using the package

A typical host application composes the package in four boundaries:

```text
HTTP / worker / connector
        ↓
presentation adapter
        ↓
authentication + authorization application services
        ↓
repository / secret / replay / crypto contracts
        ↓
host infrastructure
```

The host owns infrastructure configuration such as the SQLAlchemy engine/sessionmaker, encryption
or secret-protection implementation, key management, application configuration, routes, and
Alembic revision graph. `integration_auth` provides the reusable domain/application/security logic
and adapters around those host-owned boundaries.

### 1. Define machine permissions and resource scopes

Permissions are host-defined strings:

```text
catalog.read
catalog.write
orders.read
```

Resource scopes use the generic `type:id` model:

```text
store:store-123
organization:org-42
```

```python
from integration_auth import IntegrationResource, IntegrationScope, Permission

orders_read = Permission("orders.read")
store_scope = IntegrationScope("store", "store-123")
store_resource = IntegrationResource("store", "store-123")
```

Authorization is exact-match and fail-closed. There are no implicit wildcard or inheritance rules.

### 2. Compose persistence with a host-owned async sessionmaker

The package never creates a global `AsyncEngine` or `async_sessionmaker`.

```python
from integration_auth.infrastructure.persistence.sqlalchemy import (
    SqlAlchemyCredentialSecretProvider,
    SqlAlchemyIntegrationClientRepository,
    SqlAlchemyIntegrationCredentialRepository,
    SqlAlchemyNonceStore,
)
```

Instantiate these adapters with the host's session factory and required mapper/security
collaborators. The same persistence adapters implement the application repository contracts used
by authentication and provisioning.

Package tables are:

```text
integration_auth_clients
integration_auth_credentials
integration_auth_consumed_nonces
```

There are no foreign keys to Identity, Store, Organization, WordPress, or other host-domain tables.

### 3. Provide secret protection at the host boundary

Credential entities never contain raw secret material. The package intentionally does not ship a
hard-coded application encryption key.

The host provides the provisioning and authentication security boundaries:

```python
from integration_auth.application.contracts.provisioning import (
    CredentialSecretProtector,
    CredentialSecretUnprotector,
)
```

Provisioning stores only `ProtectedCredentialSecret`. Authentication recovers the secret only as
transient verification material.

Secure generators are available:

```python
from integration_auth.infrastructure.security import (
    SecretsCredentialSecretGenerator,
    UuidIntegrationClientIdGenerator,
    UuidIntegrationCredentialIdGenerator,
)
```

`SecretsCredentialSecretGenerator` generates 32-byte / 256-bit secrets using Python's `secrets`
module.

### 4. Compose application authentication

The application authentication flow is framework-neutral:

```text
resolve client
-> load credential candidates
-> filter usable INBOUND credentials
-> recover transient verification secret
-> verify HMAC signature
-> validate timestamp
-> atomically consume nonce
-> return IntegrationPrincipal
```

Relevant public application APIs include:

```python
from integration_auth.application import (
    AuthenticateIntegrationRequest,
    AuthenticateIntegrationRequestService,
    IntegrationAuthorizer,
)
```

Presentation adapters depend on narrow contracts instead of concrete services:

```python
from integration_auth.application.contracts.authentication import IntegrationRequestAuthenticator
from integration_auth.application.contracts.authorization import IntegrationRequestAuthorizer
```

### 5. Protect FastAPI routes

The host owns routes. `integration_auth` supplies dependencies that translate HTTP requests into the
application authentication/authorization flow.

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

The inbound integration sends:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
```

Authentication failures, malformed signed requests, bad timestamps, invalid signatures, and replay
attempts map to `401 Unauthorized` without revealing the failing detail.

### 6. Require a permission and resource scope

The host maps its HTTP/domain resource into `IntegrationResource`.

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

An authenticated integration that lacks the required permission or resource scope receives
`403 Forbidden`.

### 7. Provision and manage credentials

Provisioning services are separate from request authentication:

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

Use them from host-owned admin/application workflows to:

- register an integration client;
- assign permissions and scopes;
- issue an `INBOUND` or `OUTBOUND` credential;
- return the raw secret only at issuance/rotation time;
- rotate credentials with an explicit overlap window;
- revoke or expire credentials.

Credential direction is from the Python host's perspective:

```text
INBOUND  = external integration signs; Python host verifies
OUTBOUND = Python host signs; external integration verifies
```

Do not assume one secret is shared in both directions. Each direction can be issued, rotated,
revoked, and expired independently.

### 8. Sign outbound requests

The protocol signs exactly:

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

query = CanonicalQueryEncoder().encode(
    [("tag", "sale"), ("page", "2"), ("tag", "blue sky")]
)
assert query == "page=2&tag=blue%20sky&tag=sale"
```

Concrete HMAC/SHA-256 implementations live under infrastructure. Verification uses
`hmac.compare_digest` for constant-time comparison.

For byte-for-byte Python/PHP interoperability, see:

```text
examples/interoperability/
```

Run from the package directory:

```bash
python examples/interoperability/python_protocol.py
php examples/interoperability/php_protocol.php
python examples/interoperability/python_lifecycle_authorization.py
```

The fixtures intentionally use different inbound and outbound secrets.

## Alembic integration

The host owns the Alembic environment and revision graph. The package exposes only its metadata and
name filter:

```python
from integration_auth.migrations import (
    INTEGRATION_AUTH_TABLE_PREFIX,
    include_integration_auth_name,
    integration_auth_metadata,
)
```

Example for a host migration environment dedicated to these tables:

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

The host owns `alembic.ini`, `env.py`, revision IDs/files, branch heads, deployment ordering, and
rollback policy.

## Composing with hamresan-identity

There is no package dependency between the human and machine authentication systems.

```text
Bearer user token
    -> hamresan-identity
    -> AuthenticatedPrincipal

Signed machine request
    -> hamresan-integration-auth
    -> IntegrationPrincipal
```

A consuming application can map both to its own actor abstraction. A complete host-owned example is
available at:

```text
../examples/multi_auth_host_consumer/
```

That example keeps `identity` and `integration_auth` coupled only at the host composition boundary;
downstream application services depend only on the host-owned actor model.

## Security requirements

Production hosts must preserve these invariants:

- never log raw secrets, signatures, or canonical secret material;
- persist only protected credential secrets;
- use constant-time signature comparison;
- configure a bounded clock-skew tolerance;
- keep nonce consumption atomic;
- use transactionally atomic credential rotation;
- keep authorization exact and fail closed;
- treat `INBOUND` and `OUTBOUND` credentials independently;
- keep SQLAlchemy engine/session ownership and Alembic revisions in the host.

See `SECURITY_REVIEW.md` before deployment.

## Quality and release gates

Development gate:

```bash
make check
```

Release gate:

```bash
make release-check
```

The release gate runs lint, format checking, Pyright strict, tests/coverage, package build, isolated
wheel installation, and public API smoke imports.

The project requires branch coverage >= 85%; the current suite is substantially above that
threshold.

## Future work

Future capabilities are demand-driven rather than part of the current required architecture. They
may include Ed25519, Redis-backed replay stores, key identifiers, audit hooks, and caching.
