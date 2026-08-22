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
  - `IntegrationClientRepository` contract;
  - `IntegrationCredentialRepository` contract;
  - `CredentialSecretProvider` contract;
  - `Clock` contract;
  - inbound credential eligibility policy;
  - `AuthenticateIntegrationRequest` DTO;
  - `AuthenticateIntegrationRequestService`;
  - `IntegrationPrincipalMapper`;
  - fail-closed authentication errors;
  - support for multiple credential candidates during rotation overlap.

Not implemented yet:

- authorization services for permissions/scopes;
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

Body hashing and HMAC adapters live in infrastructure:

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

Verification uses `hmac.compare_digest` for constant-time signature comparison. Secrets and
signatures must never be logged.

## Replay protection

Stage 3 requires an atomic nonce-store boundary:

```text
consume_once(client_id, nonce, expires_at_timestamp) -> bool
```

A `(client_id, nonce)` pair may succeed only once while protected. Timestamp validation runs
before nonce consumption, so invalid stale/future requests do not pollute the replay store.
A real database-backed atomic implementation belongs to the persistence stage.

## Application authentication

Stage 4 composes the previous primitives without depending on SQLAlchemy or FastAPI.

Public application API:

```python
from integration_auth.application import (
    AuthenticateIntegrationRequest,
    AuthenticateIntegrationRequestService,
    IntegrationAuthenticationError,
)
```

Authentication infrastructure is provided through explicit contracts:

```python
from integration_auth.application.contracts import (
    Clock,
    CredentialSecretProvider,
    IntegrationClientRepository,
    IntegrationCredentialRepository,
)
```

The authentication flow is:

```text
1. resolve client_id
2. load credential candidates
3. reject credentials that are not active, inbound, owned by the client, issued, and unexpired
4. obtain transient verification material through CredentialSecretProvider
5. verify the HMAC signature
6. apply timestamp/replay protection
7. map the client identity + grants to IntegrationPrincipal
```

The service supports multiple usable credential candidates, which allows future credential
rotation to have a controlled overlap without changing the authentication orchestration.

`IntegrationCredential` still contains no raw secret. Secret retrieval is a separate boundary.
A later persistence/security adapter is responsible for obtaining verification material without
storing plaintext secrets.

Stage 4 intentionally does **not** add a Unit of Work because this read/authenticate flow has no
multi-repository transaction boundary. Atomic nonce consumption is already owned by
`NonceStore`. A UoW should be introduced later only if a concrete transactional use case needs it.

Application errors are intentionally separate from HTTP. A future presentation adapter should
map authentication failures to a generic `401 Unauthorized` without leaking client/credential
existence details.

## External integration example

An incoming integration may eventually send:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
```

HTTP header parsing belongs to the later FastAPI/presentation stage. Stage 4 expects already
translated application-level authentication input.

### PHP / WordPress interoperability

WordPress is only an example consumer. After constructing the same canonical request byte for
byte, PHP can sign with:

```php
$signature = hash_hmac('sha256', $canonicalRequest, $secret);
```

The output must be lowercase hexadecimal. A later interoperability stage will execute shared
Python/PHP vectors instead of relying only on documentation.

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

Do not assume the same credential is used in both directions. Incoming and outgoing credentials
must be independently revocable/rotatable.

## Credential rotation

Provisioning and rotation are not implemented yet. The current authentication service already
accepts multiple eligible credential candidates so a future rotation window can overlap old and
new verification credentials without rewriting the service.

Raw secrets must only cross an issuance/rotation boundary when required and must never be stored
in plaintext when persistence is implemented.

## Protecting routes

FastAPI support is not implemented yet. The future adapter should translate HTTP requests into
`AuthenticateIntegrationRequest`, call the authentication service, and later compose Stage 5
authorization.

Target behavior:

```text
invalid/missing machine authentication -> 401 Unauthorized
authenticated integration without permission -> 403 Forbidden
```

Business routes must remain thin and must not parse HMAC signatures, consume nonces, inspect
credential storage, or implement resource-scope rules directly.

## Integration with hamresan-identity

Do not add a package dependency between the two authentication systems.

```text
Bearer user token
    -> hamresan-identity
    -> UserActor

Signed machine request
    -> hamresan-integration-auth
    -> IntegrationPrincipal
```

The host may map both into its own application-specific actor abstraction.

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
