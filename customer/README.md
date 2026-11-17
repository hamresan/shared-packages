# hamresan-customer

Reusable, business-scoped customer profiles and external-identity links for Python applications.

> **Status: Customer core and profile-detail use cases implemented through Stage 3; PostgreSQL persistence, external-identity linking and HTTP adapters remain planned.** The examples use the actual Stage 3 public facade with host-injected dependencies. See [ROADMAP.md](ROADMAP.md) for stage gates.

Design references: [architecture and data ownership](docs/ARCHITECTURE.md), [public contract draft](docs/PUBLIC_CONTRACTS.md), and [security and acceptance scenarios](docs/SECURITY_AND_ACCEPTANCE.md).

## Purpose and boundaries

`hamresan-customer` provides customer records owned by a single business, without imposing a particular product, workflow, channel, authentication provider, or web framework. The same natural person may have a separate customer record in several businesses; customer data is never shared across them merely because an identity matches.

**Owns:** customer lifecycle; contacts and addresses; structured preferences; internal notes; optional links to a trusted internal identity; external identities (including messaging identifiers); tenant-scoped search and duplicate suggestions; guarded mutation and privacy erasure; typed application contracts; optional persistence and HTTP adapters.

**Does not own:** business registration or roles; authentication, OTPs or proof-of-ownership challenges; messaging connections, webhooks or conversations; appointment/order management; LLM prompts or tool routing; payment processing; cross-business customer profiles; a general-purpose CRM or event bus.

The package is designed to compose with other independently installed packages through **host-supplied adapters**. It must not import implementation classes from [`hamresan-business`](../business) or [`hamresan-identity`](../identity). A host can use those packages to implement the customer-owned authorization and identity-check contracts.

## Distribution and installation

- Distribution: `hamresan-customer`; import package: `customer`.
- Python 3.12+; standards-based `pyproject.toml` and `src/customer` layout; Hatchling build, `py.typed`, wheel and sdist.
- Lean framework-independent core. Optional extras for async SQLAlchemy, PostgreSQL (`asyncpg`), FastAPI, migration tooling and development/testing.
- Host owns the SQLAlchemy engine, connection pool, async session factory, credentials and the Alembic deployment sequence.
- No published package index release exists yet. The installable core includes Customer and profile-detail use cases. The host must inject real or fake repository implementations, authorization and other contracts; SQLAlchemy, RLS and HTTP adapters arrive in later stages.

Core installation from this monorepo now works with:

```bash
python -m pip install ./customer
```

Optional extras are declared for `sqlalchemy`, `postgres`, `fastapi` and `migrations`, but their corresponding adapters are implemented in later stages. Installing an extra does not make that future functionality available yet.

## Domain model

| Model | Responsibility and invariants |
| --- | --- |
| `Customer` | Stable UUID, immutable `business_id`, profile, status `ACTIVE / ARCHIVED / ERASED`, timestamps, optimistic `version`. A business owns many customers; a customer belongs to exactly one business. |
| `CustomerContact` | Multiple normalized `phone`/`email` values; verification provenance, optional primary per contact type. An unverified value is not proof of identity. |
| `CustomerAddress` | Multiple simple postal addresses, optional label and at most one default address. Historical snapshots in consuming applications are separate. |
| `CustomerPreference` | Simple structured key/value records, unique key per customer. Not an arbitrary secrets store or dynamic rules engine. |
| `CustomerNote` | Internal text with author and timestamp; independently authorized and hidden from ordinary customer/agent projections. |
| `CustomerIdentityLink` | Optional link to a trusted internal identity user. At most one active internal user link per customer, and at most one active customer link per `(business_id, identity_user_id)`. |
| `CustomerExternalIdentity` | Provider identity scoped by business and provider-specific account/identifier namespace; `ACTIVE / REVOKED`, verification provenance, link/revoke timestamps. Only active links resolve customers. |

All tenant-owned tables carry `business_id`. Composite foreign keys enforce matching business ownership for parent/child records; database uniqueness constraints enforce active-link and primary/default invariants under concurrency. Exact indexes, retention periods and attribute types are finalized within their implementation stages.

### Identity and channel safety

`CustomerIdentityLink` references a trusted internal user identity; `CustomerExternalIdentity` represents a provider-scoped external identifier. They are not interchangeable. The package stores **references and verified-link metadata**, not passwords, OTP codes, provider access tokens or incoming messages.

An external identity is identified by a canonical, provider-defined key including business scope and the relevant channel/account namespace. Do not assume a username, display name, claimed phone number or an unverified contact is unique or proves ownership. The host validates provider-originated assertions and performs any cross-channel challenge or verification before invoking a privileged link operation. A verified provider assertion must actually attest the needed ownership; merely presenting a phone number is insufficient.

An exact active external identity may resolve a customer. A new identity must not automatically merge with an existing customer found through name/phone similarity. Linking and relinking require authorization and trusted verification evidence. A revoked link no longer resolves customers, and erasure clears personally identifying link data according to retention policy.

## Authorization, privacy and isolation

- Every call uses a **trusted business scope** and a typed `CustomerActor` (`USER` or `SERVICE`) resolved by the host; never trust client-supplied actor, business, role or verification flags.
- `CustomerAuthorizer` is an injected contract for action-specific permissions. Human membership/branch policies remain owned by the host's business system. Service actors receive minimum permissions and do not impersonate owners.
- Sensitive operations (internal notes, identity linking, erasure) have explicit permissions; denials and cross-tenant lookups must not reveal another business's records.
- Repositories always filter by `business_id`, and PostgreSQL **row-level security (RLS)** independently constrains all customer-owned tables. The host establishes transaction-local, fail-closed tenant context on the very connection used by the unit of work. No bypass-RLS application role.
- Read projections expose only needed fields; internal notes and sensitive identifiers never appear in general-purpose or AI-facing projections by default. The host decides which authorized data to forward to third-party systems.
- Search returns business-scoped, paginated and minimally disclosed results. Exact normalized email/phone lookup, partial-name search, exact ID lookup and external-identity lookup precede any future fuzzy search. Duplicate suggestions are advisory, never an automatic merge or uniqueness rejection for unverified data.
- An external-identity resolution returns a **minimal typed `CustomerResolution`**, not the complete customer profile. Verification provenance is descriptive evidence, not a blanket grant to access unrelated resources.
- `ARCHIVED` may be reactivated with permission; `ERASED` is terminal. Erasure atomically sanitizes/removes customer-owned personal data and retains only a minimal non-identifying tombstone. A host coordinates retention and erasure across other data owners; it does not mutate historical snapshots owned elsewhere.

### Consistency and audit

The host supplies the database session factory; Customer owns its SQLAlchemy repositories, mappers and unit of work. Each Customer operation commits/rolls back its own transaction. A multi-package workflow is coordinated by the host; customer creation need not be rolled back if a separate downstream operation fails.

Sensitive mutations and their minimal audit records are written **in the same Customer transaction**, through a narrow `AuditRepository` contract implemented by the persistence adapter (potentially using a vetted third-party audit library). An audit failure prevents the mutation from committing. Audit must not retain erased personal values; actor type/id, business, subject reference, action and timestamp are typical safe metadata, subject to retention review.

`Customer.version` enables optimistic concurrency: updates include `expected_version` and fail with a typed version-conflict error on stale writes. Link uniqueness and get-or-create races additionally rely on atomic database constraints and bounded, operation-specific conflict handling.

Customer creation also accepts an **optional host-supplied `idempotency_key`**. Its scope includes business and operation; a retry with the same key and equivalent canonical request returns the previous result, while reuse with different data raises a typed `CustomerIdempotencyConflictError`. Customer creation and the idempotency record commit atomically; concurrent first requests are serialized or resolved by database uniqueness. Key records have bounded configurable retention and must not store raw personal data in request fingerprints. This works for guest creation **without** an external identity and complements (rather than replaces) external-identity uniqueness. A retry after retention expiry is not guaranteed to deduplicate; hosts must preserve keys across retries within the supported window.

### Verification freshness

External identity metadata records the **method and time** of a trusted verification, and may be updated after an authorized re-verification. `ACTIVE` means the link can resolve a customer; it does **not** guarantee that proof is fresh enough for a particular sensitive operation. The host or operation owner applies a purpose-specific freshness policy using that evidence, and can request another challenge when needed. Customer neither expires links automatically by age nor performs challenges, sends OTPs or queries messaging providers. Re-verification updates are auditable.

No domain-event bus, messaging worker, distributed transactions, automatic profile merge, or automatic schema migration is included in the initial implementation.

## Public Python API

A stable `CustomerModule` facade exposes small capability groups with typed command/query DTOs and typed errors. The public import surface is controlled through package `__init__.py` exports; consumers should not depend on internal repository or SQLAlchemy model layouts.

Implemented groups expose service objects with async `.execute(command_or_query)` methods. Other listed operations are planned:

| Group | Representative operations |
| --- | --- |
| `customers` | `create`, `get`, `update`, `search`, `archive`, `reactivate`, `erase` |
| `contacts` | `add`, `update`, `remove`, `set_primary` |
| `addresses` | `add`, `update`, `remove`, `set_default` |
| `preferences` | `set`, `list`, `remove` |
| `notes` | `add`, `list`, `remove` (separate permissions) |
| `identities` | `link`, `unlink`, `resolve` (trusted internal identities) |
| `external_identities` | `find`, `get_or_create`, `link`, `revoke`, `relink` |

The planned `CustomerResolution` projection contains `customer_id`, `business_id`, link status, `verification_method` and `verified_at`, plus an optional authorized `display_name`. It is returned only for a matching active link and an authorized lookup. Its evidence describes the stored link; caller authenticity, verification freshness and permission to view or change another resource are checked **outside** Customer by the respective host/operation owner. Avoid ambiguous claims such as `is_trusted` or `can_manage_records`.

### Example 1: Compose the module

```python
from customer import CustomerModule, CustomerModuleConfig
# The host supplies contract implementations. The package has no built-in
# database implementation until its persistence stage.
customers = CustomerModule(
    CustomerModuleConfig(
        unit_of_work_factory=customer_uow_factory,
        authorizer=customer_authorizer,  # host adapter; implements CustomerAuthorizer
        identity_verifier=identity_verifier,  # host adapter; implements IdentityVerifier
        clock=clock,  # Clock contract
        identifiers=identifier_generator,  # IdentifierGenerator contract
        creation_fingerprinter=creation_fingerprinter,  # keyed stable digest provider
    )
)
```

The composition root wires contracts explicitly. The module must not create an engine, discover dependencies through a global registry, or generate trusted actors from raw request values. The audit repository participates in the injected unit of work.

### Example 2: Create and read a guest customer

```python
from customer import CreateCustomerCommand, GetCustomerQuery

created = await customers.customers.create.execute(
    CreateCustomerCommand(
        business_id=trusted_business_id,
        actor=trusted_actor,
        display_name="Alex Rivera",
        idempotency_key=stable_host_operation_key,  # optional; reuse on retries
    )
)

profile = await customers.customers.get.execute(
    GetCustomerQuery(
        business_id=trusted_business_id,
        actor=trusted_actor,
        customer_id=created.id,
    )
)
```

A guest does **not** need an internal identity account. Contact information can be added separately with its own provenance and authorization rules.

### Example 3: Store a contact and a preference

```python
from customer import (
    AddContactCommand,
    ContactKind,
    SetPreferenceCommand,
)

contact = await customers.contacts.add.execute(
    AddContactCommand(
        business_id=trusted_business_id,
        actor=trusted_actor,
        customer_id=created.id,
        kind=ContactKind.EMAIL,
        value="alex@example.com",
        is_primary=True,
    )
)

preference = await customers.preferences.set.execute(
    SetPreferenceCommand(
        business_id=trusted_business_id,
        actor=trusted_actor,
        customer_id=created.id,
        key="language",
        value="en",
    )
)
```

Contact creation does **not** establish verified ownership. Internal notes are available only through `customers.notes` with separately granted `customer.notes.read` and `customer.notes.write` permissions. Basic profile projections never contain notes.

### Example 4: Resolve an external identity without implicit creation (illustrative; Stage 4)

```python
from customer import FindCustomerByExternalIdentityQuery

resolution = await customers.external_identities.find(
    FindCustomerByExternalIdentityQuery(
        business_id=trusted_business_id,
        actor=trusted_service_actor,
        provider="telegram",
        channel_account_id=trusted_channel_account_id,
        external_user_id=trusted_provider_user_id,
    )
)

# A missing match returns None; no customer is created.
# A match is a minimal CustomerResolution with link verification metadata.
# The host still checks whether that evidence is recent enough for its operation.
# An explicitly authorized get_or_create operation is a separate call.
```

Provider authentication and any proof-of-control challenge occur **before** the host calls link/relink. A newly observed identifier does not prove that it belongs to an existing customer. A lookup is also not sufficient authorization to disclose private history.

### Example 5: Handle a stale update

```python
from customer import CustomerVersionConflictError, UpdateCustomerCommand

try:
    await customers.customers.update.execute(
        UpdateCustomerCommand(
            business_id=trusted_business_id,
            actor=trusted_actor,
            customer_id=profile.id,
            expected_version=profile.version,
            display_name="Alex R.",
        )
    )
except CustomerVersionConflictError:
    # Refresh the profile and ask the caller to review conflicting edits.
    pass
```

The examples for Customer and profile details use implemented APIs with host-supplied dependencies. External identity lookup remains a **future** feature; never import that illustrative Stage 4 query until implemented.

## Persistence, migrations and test expectations

- PostgreSQL is the production acceptance database; SQLAlchemy 2 async is an optional adapter. The framework-independent core has no SQLAlchemy/FastAPI imports.
- Package-owned `customer_*` tables, metadata exposure and Alembic integration helpers compose with other package metadata. The **host** runs reviewed migrations during deployment, never automatically during application startup.
- Migration work includes RLS policies and `WITH CHECK` coverage, transaction-local tenant context, composite tenant foreign keys, active-link uniqueness, indexes and a non-bypass database role. SQLAlchemy metadata alone cannot express all required RLS DDL.
- Tests mirror source responsibilities. Unit tests use explicit fakes; integration tests exercise SQLAlchemy and real PostgreSQL; CI proves isolation, concurrency, rollback-on-audit-failure, migration upgrade and wheel installation.
- Use Ruff, strict Pyright, pytest/pytest-asyncio, coverage and a reproducible development lockfile.

## Development status

Stages 0–2 are complete. Stage 3 core and profile-detail logic has passed local automated checks and awaits GitHub CI/review. PostgreSQL persistence, transaction-level audit, RLS and external identity linking are future stages; the current in-memory fakes are only for tests. See [ROADMAP.md](ROADMAP.md) for stage gates and current status.
