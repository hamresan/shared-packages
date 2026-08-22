# hamresan-integration-auth

Reusable machine-to-machine authentication and authorization package for Python applications.

```text
Distribution: hamresan-integration-auth
Import:       integration_auth
Python:       >= 3.12
```

`hamresan-integration-auth` is intended for trusted application integrations, plugins, connectors, partner APIs, internal services, workers, and agents that need to authenticate requests and authorize actions without pretending that a machine is a human user.

Typical examples:

```text
Python backend ↔ WordPress plugin
Python backend ↔ Shopify connector
API ↔ partner application
service ↔ service
backend ↔ desktop/edge agent
```

The package is deliberately separate from `hamresan-identity`:

- `hamresan-identity` authenticates human users and user sessions.
- `hamresan-integration-auth` authenticates machine/integration clients and evaluates their permissions/scopes.
- a host application may use both and map them into its own higher-level actor abstraction.

The package must not depend on WordPress, WooCommerce, Identity, Store, Subscription, or any provider-specific SDK.

> Status: Stage 1 core domain is implemented. Authentication, HMAC signing, replay protection, persistence, authorization services, credential provisioning, and FastAPI integration shown below remain target APIs implemented incrementally according to `ROADMAP.md`.

## Available API — Stage 1

The current public API provides the domain model only:

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

Example authorization facts:

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
    scopes=frozenset(
        {
            IntegrationScope("store", "store-123"),
        }
    ),
)
```

Credential metadata is intentionally separate from cryptographic material:

```python
credential = IntegrationCredential(
    credential_id=IntegrationCredentialId("credential-1"),
    client_id=IntegrationClientId("wp_store_123"),
    direction=CredentialDirection.INBOUND,
    status=CredentialStatus.ACTIVE,
    issued_at=issued_at,
)
```

`IntegrationCredential` does not contain a raw secret. Cryptographic material and signing/verifying behavior belong to later crypto/application stages.

Credential direction is defined from the Python host application's perspective:

```text
INBOUND  = external integration signs; Python host verifies
OUTBOUND = Python host signs; external integration verifies
```

The current lifecycle policy permits:

```text
ACTIVE → REVOKED
ACTIVE → EXPIRED
```

`REVOKED` and `EXPIRED` are terminal states in the Stage 1 domain model.

## Core concepts

```text
IntegrationClient
    │
    ├── permissions
    │      ├── catalog.read
    │      ├── catalog.write
    │      └── orders.read
    │
    └── scopes
           ├── store:store-123
           └── organization:org-42

IntegrationCredential
    ├── client_id
    ├── direction
    └── lifecycle status
```

Authentication answers:

```text
Who is calling?
```

Authorization answers:

```text
What may this integration do?
On which resource or scope may it do it?
```

Those are separate responsibilities.

## Planned request authentication

The first planned request-authentication mechanism is HMAC-SHA256 signing. It is not implemented in Stage 1.

A signed request will carry values such as:

```text
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0...
X-Integration-Signature: ...
```

The signature will be calculated over a canonical request rather than only the body:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

Conceptually:

```text
signature = HMAC_SHA256(secret, canonical_request)
```

Timestamp validation plus one-time nonce consumption will provide replay protection.

The architecture keeps signing behind contracts so Ed25519 or another asymmetric implementation can be added later without changing application services.

## Why not use user JWTs for integrations?

A WordPress plugin or external connector is not a human user session. Reusing human access tokens usually creates the wrong ownership and lifecycle model:

```text
human login lifecycle != integration credential lifecycle
human permissions       != connector permissions
user revocation          != integration credential rotation
```

Machine credentials therefore have their own identity, permissions, scopes, rotation, revocation, and audit lifecycle.

# Using the package inside another project

The most important rule is that domain packages such as Store, Catalog, Orders, or Subscription should not depend directly on `integration_auth`.

Prefer composition at the host application boundary:

```text
                    Host Application
                    /              \
                   /                \
        domain/package          integration_auth
        Store / Orders          authentication
        own contracts           authorization
```

This prevents machine-auth concerns from leaking into reusable business packages.

## 1. Authenticate an incoming integration request

The target application API will expose a request authenticator that produces an integration principal. The authentication service is not implemented yet.

Target usage:

```python
from integration_auth import IntegrationPrincipal
from integration_auth.application import AuthenticateIntegrationRequestService

principal: IntegrationPrincipal = await authenticator.authenticate(request_data)
```

`IntegrationPrincipal` itself is available now and represents the authenticated machine identity, not a user:

```python
from integration_auth import IntegrationClientId, IntegrationPrincipal, IntegrationScope, Permission

principal = IntegrationPrincipal(
    client_id=IntegrationClientId("wp_store_123"),
    permissions=frozenset(
        {
            Permission("catalog.read"),
            Permission("catalog.write"),
            Permission("orders.read"),
        }
    ),
    scopes=frozenset(
        {
            IntegrationScope("store", "store-123"),
        }
    ),
)
```

The principal contains authorization facts; it does not contain WordPress-specific behavior.

## 2. Protect a route by permission

Route-level authorization and FastAPI dependencies are target APIs for later roadmap stages.

Target FastAPI usage:

```python
@router.post(
    "/products",
    dependencies=[Depends(require_integration_permission("catalog.write"))],
)
async def create_product(request: CreateProductRequest) -> ProductResponse:
    return await create_product_service.execute(request)
```

Expected behavior:

```text
invalid/missing integration authentication → 401 Unauthorized
valid integration but missing permission  → 403 Forbidden
```

The business route remains thin and does not parse signatures or inspect credential storage.

## 3. Authorize access to a specific resource

Permission alone is not sufficient for multi-tenant resources.

Example:

```text
permission: orders.read
scope:      store:store-123
```

An integration with `orders.read` for `store-123` must not automatically read orders owned by `store-456`.

`IntegrationResource` is available in Stage 1. The authorization service shown below is planned for the authorization stage.

Target authorization usage:

```python
await integration_authorizer.require(
    principal=principal,
    permission="orders.read",
    resource=IntegrationResource(
        resource_type="store",
        resource_id="store-123",
    ),
)
```

Resource authorization is usually performed after the application has resolved the target resource. Do not put ownership checks such as this directly into route code:

```python
# Avoid this pattern:
if principal.store_id != order.store_id:
    raise HTTPException(...)
```

Use a dedicated authorization component/policy instead.

## 4. Connect Integration Auth to another reusable package

Suppose a Store package owns this narrow contract:

```python
class StoreAuthorizer(Protocol):
    async def require_store_access(self, actor: StoreActor, store_id: str) -> None: ...
```

The Store package should not import `integration_auth`.

The host implements an adapter in its composition root:

```text
IntegrationPrincipal
        ↓
host StoreAuthorizer adapter
        ↓
Store package contract
```

This keeps both packages independent.

## 5. Routes callable by both users and integrations

A host may expose the same business operation to dashboard users and machine integrations.

Do not merge the two authentication systems.

Use them side by side:

```text
Bearer user token
    ↓
hamresan-identity
    ↓
UserActor

Signed machine request
    ↓
hamresan-integration-auth
    ↓
IntegrationActor
```

The host can then map both into its own canonical actor type:

```text
Actor
├── actor_type = user
└── actor_id   = user-123

Actor
├── actor_type = integration
└── actor_id   = wp_store_123
```

Business modules may depend on that host/package-specific actor contract rather than on either authentication implementation.

# External integration usage

## WordPress plugin ↔ Python backend

WordPress is only one consumer of the protocol.

The package itself must not contain classes such as:

```text
WordPressClient
WooCommerceCredential
WordPressPermission
```

Instead it exposes generic integration concepts.

A host may eventually provision credentials for a WordPress plugin:

```text
client_id: wp_store_123
secret:    generated high-entropy secret
scopes:    store:store-123
permissions:
    catalog.read
    catalog.write
    inventory.read
    inventory.write
    orders.read
```

Credential provisioning and secret storage are not implemented in Stage 1.

### Plugin → backend

Planned request example:

```http
POST /api/catalog/products
X-Integration-Client-Id: wp_store_123
X-Integration-Timestamp: 1787390042
X-Integration-Nonce: 7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3
X-Integration-Signature: <signature>
Content-Type: application/json

{"sku":"SKU-1","stock":5}
```

The backend will eventually perform:

```text
1. resolve client_id
2. load active credential
3. validate timestamp tolerance
4. consume/check nonce
5. hash request body
6. rebuild canonical request
7. verify signature
8. build IntegrationPrincipal
9. check required permission
10. check resource scope when required
11. execute business use case
```

### PHP signing concept

The future canonical protocol is intended to interoperate with PHP HMAC functions. Conceptually:

```php
$bodyHash = hash('sha256', $body);
$canonical = implode("\n", [
    $method,
    $pathAndQuery,
    $timestamp,
    $nonce,
    $bodyHash,
]);
$signature = hash_hmac('sha256', $canonical, $secret);
```

The final implementation will define exact encoding, header names, query canonicalization, signature encoding, and constant-time verification. External consumers must follow that canonical specification exactly.

## Backend → WordPress plugin

Communication is two-way, so the backend must not reuse the plugin's incoming credential blindly.

The Stage 1 `CredentialDirection` model supports separate credentials from the host perspective:

```text
INBOUND
    external integration signs
    Python backend verifies

OUTBOUND
    Python backend signs
    external integration verifies
```

Each direction can later be rotated or revoked independently.

The receiving external endpoint will apply the same verification concerns: timestamp, nonce, canonical request, signature, and permission/scope policy appropriate to that endpoint.

## Replay protection

A valid captured request must not be reusable.

The future verifier will therefore check both:

```text
timestamp tolerance
nonce uniqueness
```

Example policy:

```text
accepted clock skew: ±5 minutes
nonce: usable once per client inside replay window
```

Exact defaults will be established in the relevant roadmap stages and remain configurable through explicit policy objects rather than hidden constants.

## Credential rotation

Stage 1 defines lifecycle states and valid terminal transitions:

```text
ACTIVE
REVOKED
EXPIRED
```

Provisioning and rotation behavior belongs to a later roadmap stage and should support overlap where necessary:

```text
credential v1 ───── active ─────┐
                                ├── short overlap
credential v2             ──────┴──── active
```

This allows an integration and backend to deploy a new secret without downtime.

The package must never log raw secrets or signatures.

## Permissions and scopes

Permission vocabulary is consumer-defined.

Examples:

```text
catalog.read
catalog.write
inventory.read
inventory.write
orders.read
orders.write
subscription.read
```

Scopes constrain where those permissions apply:

```text
store:store-123
organization:org-42
workspace:workspace-a
```

Stage 1 implements generic validated `Permission`, `IntegrationScope`, and `IntegrationResource` value objects. The package does not need to understand what a Store or Organization actually is.

# Package architecture

```text
integration_auth/
├── domain/                       # Stage 1 implemented
│   ├── entities/
│   ├── enums/
│   ├── policies/
│   ├── validators/
│   └── value_objects/
│
├── application/                  # later stages
│   ├── contracts/
│   ├── dto/
│   ├── mappers/
│   └── services/
│       ├── authentication/
│       ├── authorization/
│       └── credentials/
│
├── infrastructure/               # later stages
│   ├── crypto/
│   │   └── hmac/
│   └── persistence/
│       └── sqlalchemy/
│
├── migrations/                   # later stage
│
└── presentation/                 # later stage
    ├── dependencies/
    ├── mappers/
    ├── routes/
    └── schemas/
```

Tests mirror production responsibilities:

```text
tests/
├── domain/
├── application/
├── infrastructure/
├── migrations/
├── presentation/
└── support/
```

Fake, Builder, Factory and Test Helper components with independent responsibility belong in `tests/support/...`, not inside test functions/files.

# Architectural rules

The implementation must follow these rules throughout the roadmap:

- Clean Architecture and SOLID boundaries are mandatory.
- Business services remain thin workflow orchestrators.
- Mapping belongs to mappers, not private service helpers.
- Validation belongs to dedicated validators/policies when independently meaningful.
- Cryptographic operations belong to crypto/signer/verifier components.
- Persistence stays behind repositories and Unit of Work contracts.
- Provider/framework-specific code stays in adapters.
- Dependencies are explicit and injected; no Service Locator.
- Implementations explicitly implement/inherit their contracts where practical.
- No direct dependency on `hamresan-identity`.
- No WordPress-specific domain model.
- No raw secret logging.
- No global SQLAlchemy engine/sessionmaker.
- Alembic revision history is host-owned.
- `__init__.py` exposes controlled public package APIs to avoid long internal import paths without creating heavy circular barrel imports.
- Tests mirror source responsibility/layer structure.
- Pyright strict, Ruff, Ruff format, pytest and branch coverage ≥85% remain quality gates.

# Development

```bash
cd integration_auth
python -m pip install -e ".[test]"
make check
```

See `ROADMAP.md` for the staged implementation plan.
