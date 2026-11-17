# Optional FastAPI integration

Install `hamresan-customer[fastapi,postgres]` when using the optional HTTP router.
The package has no HTTP server, session middleware, login endpoint, or provider webhook.

## Host composition

```python
from fastapi import Depends, FastAPI, Header, HTTPException

from customer import CustomerActor, CustomerModule
from customer.presentation.http import create_customer_router

# Compose CustomerModule in the host's application startup using the real
# SQLAlchemyCustomerUnitOfWorkFactory, authorization, verification, clock,
# identifier, creation fingerprint and retention policy adapters.
customer_module: CustomerModule = build_customer_module_from_host_dependencies()

async def authenticate_actor(authorization: str | None = Header(default=None)) -> CustomerActor:
    principal = await trusted_authentication_backend.authenticate(authorization)
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    # Resolve membership/service access using trusted host records.
    return await trusted_business_access.to_customer_actor(principal)

app = FastAPI()
app.include_router(create_customer_router(customer_module, authenticate_actor))
```

The `build_customer_module_from_host_dependencies`, `trusted_authentication_backend`
and `trusted_business_access` symbols above are host-provided integration points,
not package APIs. The host must inject a verified `CustomerActor` including a trusted
business ID; the router never accepts actor type, actor ID or permissions from JSON.
The path business ID must match that actor's authorized business scope, checked again
inside Customer application services. A multi-business user must select an authorized
business through the host's authenticated context.

## Routes

| Method | Path under `/businesses/{business_id}/customers` | Action |
| --- | --- | --- |
| POST | `/` | Guest/customer creation; optional `Idempotency-Key` header |
| GET | `/{customer_id}` | Authorized minimal customer projection |
| PATCH | `/{customer_id}` | Update display name with `expected_version` |
| POST | `/identities/resolve` | Exact authorized lookup with `provider`, `channel_account_id`, `external_user_id` JSON fields |

Example guest creation (the host must authenticate and authorize the caller):

```http
POST /businesses/11111111-1111-4111-8111-111111111111/customers
Authorization: Bearer <host-issued-token>
Idempotency-Key: external-operation-42
Content-Type: application/json

{"display_name": "Alex Rivera"}
```

Use the same key and payload on retries. A divergent payload with the same key
returns `409 idempotency_conflict`; a stale update version returns
`409 version_conflict`. The response includes only business/customer IDs, display
name, status, version and timestamps. No contacts, addresses or internal notes.

## Trusted external identity resolution

1. Host verifies the incoming provider event, channel/account namespace and sender.
2. Host authenticates its service actor with the minimal lookup permission.
3. Host calls the exact external identity lookup using the verified provider key.
4. Host verifies link-evidence freshness for the requested downstream operation.
5. The downstream record owner independently authorizes customer-scoped access.

`CustomerResolution` is **not** an access token. It never grants permission to view,
reschedule, cancel or delete records in another subsystem. Missing or inaccessible
customers return the same generic `404 customer_unavailable` response, including
cross-business authorization failures. The lookup uses POST to keep external
identifiers out of URL access logs. The host must also redact request-body logs.

To link a new messaging identity, the host first obtains verified ownership evidence
and invokes the public `LinkExternalIdentityCommand` through the Python facade.
Verification codes, transport, rate limiting and challenges remain outside Customer.
Do not create a customer merely because a provider message arrived.

## Database and deployment

Use the host's async PostgreSQL session factory and Customer UoW. Apply the package
metadata and RLS policy via host-controlled Alembic migration revisions; compose
metadata with other packages and never run schema creation at request time. Runtime
connections use a non-owner/non-BYPASSRLS role with transaction-local tenant scope.
The Customer UoW sets and clears the tenant transaction context. Configure pool
recycling and migration order in the host, not in the HTTP adapter.

Least-privilege service actors should normally have `customer.read` and exact
external-identity lookup rights only. Internal notes, linking, erasure and other
mutations require independently granted permissions. Never grant them by default.
