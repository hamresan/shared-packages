# Customer public contracts — Stage 0 draft

> **Status:** Proposed version 1 contract surface for review. Names and example shapes are not yet executable. Public names are frozen at the Stage 1 gate only after typed implementation tests.

## Public entry point

The host constructs one `CustomerModule` via explicit `CustomerModuleConfig` dependencies. Stable named capability groups expose async use cases; domain and application packages never import concrete SQLAlchemy or FastAPI implementations. This is a grouped facade, not a large multi-responsibility service.

The config includes a `CustomerUnitOfWorkFactory`, `CustomerAuthorizer`, `IdentityVerifier` (validity and accepted evidence for internal-link operations), and narrow clock/identifier/normalization components as justified. The host injects a configured SQLAlchemy adapter if it opts into persistence. Audit is a repository available inside the Customer UoW, not a separate auto-committing network logger.

## Trusted context

Every scoped operation accepts a trusted `business_id` and `CustomerActor`, as established by the host:

| Field | Meaning |
| --- | --- |
| `business_id: UUID` | Validated business scope, immutable for an existing customer. |
| `actor_id: UUID | str` | Stable, host-authenticated principal reference; not a raw sender-supplied subject. |
| `actor_type: USER | SERVICE` | Distinguishes human member from service principal for authorization and minimal audit. |

Avoid confusing *identity lookup* with permission to read a private profile. `CustomerAuthorizer` checks an action and resource scope, and may use trusted host Business membership/branch policies for `USER` and host service permissions for `SERVICE`. All decisions fail closed. Do not use customer input as a role, verified status or business authority.

## Capability groups and operation contracts

| Capability | Operations | Specific behavior |
| --- | --- | --- |
| `customers` | `create`, `get`, `update`, `search`, `archive`, `reactivate`, `erase` | Tenant-scoped, authorized, typed projection; update requires `expected_version`; erasure terminal. |
| `contacts` | `add`, `update`, `remove`, `set_primary` | Normalize email/phone; verification evidence is host-trusted. |
| `addresses` | `add`, `update`, `remove`, `set_default` | At most one default. |
| `preferences` | `set`, `list`, `remove` | Simple per-customer unique keys and values. |
| `notes` | `add`, `list`, `remove` | Restricted access distinct from basic profile permission. |
| `identities` | `link`, `unlink`, `resolve` | Optional trusted internal identity user reference; no auth or OTP here. |
| `external_identities` | `find`, `get_or_create`, `link`, `revoke`, `relink`, `record_verification` | Exact provider-scoped lookup; explicit creation; evidence-based linking; active/revoked lifecycle. |

### `CustomerResolution`

`find_by_external_identity` returns `CustomerResolution | None` when the caller has permission. A minimal result contains:

| Field | Type (draft) | Meaning |
| --- | --- | --- |
| `customer_id` | `UUID` | Stable business-scoped Customer reference. |
| `business_id` | `UUID` | Owner business. |
| `identity_status` | `ACTIVE` | Only active links are resolvable. |
| `verification_method` | `str | None` / constrained enum after review | Method of last accepted verification evidence. |
| `verified_at` | UTC-aware `datetime | None` | Time of the accepted verification; a null value must not be represented as verified. |
| `display_name` | `str | None` | Included only under explicitly authorized minimum projection. |

No raw phone, provider token, internal note, address, full contact list, universal `is_trusted` flag or operation-specific permission is included. `CustomerResolution` does **not** say whether a caller can view or mutate another application's resource. The host authenticates the inbound request and the resource-owning application independently authorizes its own operation, possibly requiring newer proof than `verified_at`.

### Creation idempotency

`CreateCustomerCommand` has optional opaque `idempotency_key`. The host preserves the **same key** across retries of the same logical create operation; no key means no general-purpose replay guarantee. Keys are scoped at least by `(business_id, operation)` and subject to configured bounded retention.

- First valid request: create customer and store key + canonical request fingerprint + stable resulting customer reference in the same transaction.
- Retry with same key and semantically equivalent normalized request: return the original creation result without a second insert.
- Same key with materially different request: raise `CustomerIdempotencyConflictError` without changing data.
- Concurrent first requests: unique database constraint and transactional conflict handling produce one customer; uncertain write outcome must be resolved through persisted idempotency lookup, not blind duplicate creation.
- Retention expiry: automatic replay protection no longer promised. The retention duration and cleanup mechanism remain explicit configuration and acceptance criteria.
- Request fingerprint uses deterministic canonical fields and a privacy-preserving keyed digest rather than storing raw personal fields; key rotation/retention behavior must be documented in Stage 5.

External-identity get-or-create also relies on its own active-identity uniqueness independent of this optional key. The two mechanisms solve different duplication causes.

## Command results and errors

Public DTOs are immutable or otherwise safely typed and do not expose ORM instances. No `HTTPException`, SQLAlchemy `IntegrityError`, external provider error or framework object crosses the application API.

Error taxonomy (draft public names):

| Error | Semantic condition |
| --- | --- |
| `CustomerError` | Base for documented customer domain/application errors. |
| `CustomerNotFoundError` | Missing or inaccessible customer; do not reveal another tenant's existence. |
| `CustomerPermissionDeniedError` | Unauthorized operation without sensitive disclosure. |
| `CustomerValidationError` | Invalid canonical input or operation precondition. |
| `CustomerVersionConflictError` | Expected profile version is stale. |
| `CustomerIdentityConflictError` | Active internal/provider identity association conflict. |
| `CustomerIdempotencyConflictError` | Same idempotency key reused for a different logical request. |
| `CustomerErasedError` | Operation forbidden against a terminally erased record, when disclosure is authorized. |

Where existence itself is sensitive, map errors to the same safe external response. Presentation adapters perform HTTP mappings; the package's domain/application layers remain transport-neutral.

## Authorization scope (minimum action taxonomy)

Proposed stable actions include `customer.read`, `customer.create`, `customer.update`, `customer.archive`, `customer.erase`, `customer.notes.read`, `customer.notes.write`, `customer.identity.link` and `customer.external_identity.manage`. More granular contact/address permissions should be added only where a consuming host requires separate policy. Service actors start with least privilege; none receive inherited owner permissions by default.

## Versioning

Use a documented version-1 public API, SemVer releases and explicit breaking-change review. `__init__.py` exports only intentional public types and entry points; internal mappers/models/services are not stable imports. Source-code examples in the README are illustrative until Stage 1 binds these names to tested implementations.
