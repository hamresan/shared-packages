# hamresan-business

Reusable business, branch, and organization-membership management for Python applications.

> **Status: Stage 7 hardening in progress.** Stages 1–6 are implemented and merged. The source is locally installable; no distribution has been published. The corrected PostgreSQL ownership-transfer concurrency test passed on a developer's live database; GitHub CI verification remains pending.

## Purpose

`hamresan-business` provides a reusable foundation for applications that manage one or many businesses, each with zero, one, or multiple branches. An individual can own or participate in multiple businesses without a one-business-per-user restriction.

The package manages business organization and access relationships; it does not implement authentication, staff scheduling, payroll, commerce, or other application-specific operations.

## Supported organization models

| Scenario | Expected behavior |
| --- | --- |
| Single-location business | One `Business` with one `Branch`; no special single-branch model needed. |
| Multi-branch business | One `Business` with multiple independently identified branches. |
| Multiple businesses per individual | One identity can own or belong to multiple distinct businesses. |
| Multiple users per business | Exactly one active `Owner`, any number of `Manager` and `Member` users. |
| Non-physical organization | A `Business` can exist before a branch is created; zero branches is valid during setup. |

The business-to-branch relationship is one-to-many. The user-to-business relationship is many-to-many through memberships. Ownership is **a membership role**, not an exclusive `owner_user_id` column or a unique constraint on `user_id`. A business has one active Owner through the supported use cases; a database index prevents a second active Owner. The same user may own several different businesses.

## Core models and access extensions

### Business

The organizational and tenant root. Initially includes a stable UUID, name, optional business type/category, country, default language/currency, lifecycle status, and timestamps. A business is not automatically a physical location.

### Branch

Belongs to exactly one business and has its own UUID, name, optional address/contact details, IANA timezone, active/archived status, and timestamps. Branch settings override business defaults only where explicitly supported. Historical branch references must remain stable when a branch is archived.

### BusinessMembership

Links an external identity `user_id` to a business, with a role and membership status. Roles are `Owner`, `Manager`, and `Member`. Ownership changes only through an atomic transfer to another active member. The former Owner becomes a Manager.

### Branch access (narrow extension)

Some applications need to restrict a member to selected branches. `BranchAccessScope.ALL` gives an active member access to the business's branches; `BranchAccessScope.SELECTED` uses an explicit membership-to-branch association. **An empty selected list means zero accessible branches**, not unrestricted access. Owners and Managers always have full branch visibility. Every selected branch ID is validated against the membership's business before the change is committed.

## Employee management boundary

The package distinguishes **organization membership** from **employment**:

- **In scope:** authenticated users' memberships, owner/manager/member roles, invitation and membership status, and optional access to specific branches.
- **Out of scope:** employee records without user accounts, contracts, payroll, attendance, leave, professional qualifications, shift planning, resource capacity, and operational assignments.

An employee may not have a login, and a business member may not be an employee. Keeping these concepts separate prevents unrelated applications from inheriting a workforce-management system. Applications can build their own staff domain or use a dedicated workforce package when there is proven shared demand.

## Authentication and notifications

`hamresan-business` **does not issue OTPs, authenticate passwords/tokens, or send messages itself**.

- [`hamresan-identity`](../identity) handles registration/login using email or mobile OTP, sessions, access tokens, revocation, and authenticated principals.
- [`hamresan-notification`](../notification) provides notification contracts and delivery infrastructure; Identity uses its `NotificationSender` for OTP delivery.
- The **host application** composes Identity and Notification, authenticates each request, and converts the trusted principal into a small Business-owned `AuthenticatedActor` contract.
- Business use cases enforce membership and resource authorization. Raw `user_id`, role, or ownership supplied by a request body is never authoritative.
- Future invitation notifications may be dispatched through an injected notification contract or a host-owned integration; this package must not create its own notification worker or OTP flow.

The domain/application core remains independent of concrete Identity and Notification implementations. The [consumer example](../examples/identity_business_consumer) demonstrates their composition with a real JWT/session implementation rather than an example-only token stub.

## Package boundaries

**Owns:** business and branch lifecycle, membership and ownership, scoped business/branch access policies, typed public contracts, persistence adapters, and optional FastAPI integration.

**Does not own:** user identities and credentials, OTP transport, employee HR records, inventory, service catalogs, operations, scheduling, billing, or application-specific roles and permissions.

The existing [`hamresan-store`](../store) remains a separate package. Do not silently modify its persistence model or force its one-store-per-owner policy into `hamresan-business`. Generic concepts may be reused carefully where they truly match; the packages should not depend on each other's internal implementations.

## Architecture principles

- Python 3.12+, `pyproject.toml`, `src/` layout, installable distribution `hamresan-business` and public import package `business`.
- Clean Architecture and SOLID: domain and application independent of FastAPI, SQLAlchemy, and external authentication implementations.
- Explicit contracts, injected dependencies, small single-responsibility policies, validators, mappers, factories, and repositories.
- Async SQLAlchemy persistence using a **host-provided** session factory; prefix package-owned tables with `business_`.
- Host-owned Alembic revision history; expose metadata and inclusion helpers rather than managing host migrations implicitly.
- Stable UUID identities; `user_id` is an external reference with no cross-package foreign key to Identity tables.
- Tenant and branch ownership are checked deterministically, including updates and membership changes. Never trust tenant scope from an unverified request.
- Test directories mirror the source structure. Independent test doubles and builders live in separate support modules.
- Ruff, strict Pyright, pytest unit/integration tests and reproducible CI gates; use `uv` for dependency locking and development.

## Implemented application core (Stages 1–4)

The package exposes framework-independent primitives and use cases:

- `AuthenticatedActor` is a trusted, host-resolved user identity; commands never accept
  an owner ID or role as proof of authorization.
- `CreateBusinessService` creates a business and its active owner membership within
  one injected unit of work. The persistence adapter must commit both atomically.
- `GetBusinessService` and `ListBusinessesService` return only businesses visible to
  the actor through active membership.
- `UpdateBusinessService` and `ArchiveBusinessService` require an active owner role.
  An archived business can still be read, but cannot be edited or archived twice.
- `CreateBranchService`, `GetBranchService`, `ListBranchesService`,
  `UpdateBranchService`, `ArchiveBranchService`, and `ReactivateBranchService`
  manage zero, one, or many branches within their parent business.
- `BranchAddress` includes optional `city` and `country_code`, and `BranchContact`
  supports optional phone/email. A physical address is not required to create a branch.
- Branch creation, updates, archival, and reactivation require an active business
  Owner or Manager and a non-archived parent business. Active business members can read its
  branches within the member's configured branch access scope.
- A branch's `business_id` is never mutable through the public use cases.
  Cross-business branch lookup and write operations are rejected, and archived
  branches remain readable with stable IDs.
- Branch listing supports optional case-insensitive city and country-code filters.
- `InviteMemberService` creates an invitation for a known external user ID (without
  issuing credentials or sending messages); `AcceptMembershipService` accepts it
  only for that trusted actor. Invited users cannot read business resources.
- `ListMembershipsService`, `ChangeMemberRoleService`, `RevokeMembershipService`
  and `SetMemberBranchAccessService` are Owner-only operations. General role changes
  switch between Manager and Member; Manager has full branch visibility and Member
  starts with an empty selected list when demoted.
- `TransferOwnershipService` is the only supported way to change Owner. The
  recipient must be an active member of that business. The former Owner becomes
  a Manager, both role updates and the audit entry commit atomically, and the
  current Owner cannot be revoked or demoted through ordinary membership operations.
- Membership changes and branch assignments are committed together with
  structured `MembershipAuditRecord` entries. A revoked user can be re-invited
  as a new membership while historical revoked memberships remain recorded.

The public business profile update is a **full profile replacement** (`name` and
`business_type`); passing `business_type=None` explicitly clears it. Country,
language, and currency settings are retained by profile updates.

`UpdateBranchCommand` also uses explicit full replacement semantics for `name`,
`timezone`, optional `address`, and optional `contact`. Pass `None` explicitly to
clear an address or contact. Branches require a valid IANA timezone and do not
inherit a default timezone implicitly.

The application services require injected `BusinessUnitOfWorkFactory`, factories,
validators, policies, and clocks. Stages 2–4 tests exercise those use cases against an
explicit in-memory implementation of the repository/unit-of-work contracts.
Async SQLAlchemy repositories and a database-backed Unit of Work are available
as the optional `sqlalchemy` extra. The SQL adapter uses an injected async
session factory; `commit()` persists the entire unit of work, and leaving
without commit rolls it back. A partial unique index rejects duplicate current
(`active`/`invited`) memberships while preserving revoked membership history.

The membership-change lock uses PostgreSQL `SELECT ... FOR UPDATE` on the
business row, and owner authorization is rechecked after taking the lock to
avoid a stale-permission race. A partial database index also prevents two
active Owners in the same business. SQLite supports functional/integrity tests but
does **not** provide equivalent row-lock semantics. PostgreSQL concurrency
tests require `BUSINESS_TEST_POSTGRES_DSN`; GitHub Actions provisions a
PostgreSQL service for them.

### Stage 4 membership semantics

- The host authenticates actors and validates that invitation targets are
  legitimate Identity users; the Business package does not perform identity lookup.
- Invitees start with `Member`, `Invited`, and `Selected` with **no** branch IDs.
  An owner must explicitly grant access before a newly accepted invitee can
  view branch records. Revoked identities have no current membership access.
- Membership changes serialize within the PostgreSQL unit of work through
  `lock_business_membership(business_id)`. Re-invitation preserves history and
  enforces only one current active/invited membership per user and business.

### Persistence composition (Stage 5)

Install `pip install hamresan-business[sqlalchemy]` for the SQL adapter, or
`hamresan-business[postgres]` for the asyncpg PostgreSQL driver as well.
The host supplies its own `async_sessionmaker[AsyncSession]`; construct a
`SqlAlchemyBusinessUnitOfWorkFactory` with the injected session factory and
`BusinessMapper`, `BranchMapper`, `MembershipMapper` and
`MembershipAuditMapper`. No global engine is created by the package.

The host owns Alembic migrations. Use `business.migrations.business_metadata()`
and `include_business_name` when composing metadata and reflection with other
packages. All five package tables use the `business_` prefix. Preserve
foreign-key constraints (including composite business-scoped membership/branch
associations) and the partial unique membership index during migrations.

SQLite integration tests run by default; set `BUSINESS_TEST_POSTGRES_DSN` to a
dedicated test database URL to exercise the PostgreSQL concurrency scenario.
Each PostgreSQL test uses and drops its own uniquely named schema.

### FastAPI composition (Stage 6)

Install the optional `hamresan-business[fastapi]` extra. Build business, branch
and membership use cases via `BusinessApplicationFactory` using the injected
Unit of Work, clock, and identifier generator. Then pass the explicit use-case
groups and a trusted `AuthenticatedActorDependency` to
`business.presentation.build_fastapi_business_adapter(...)` and call
`adapter.install(app)`. Business never validates JWTs or issues OTPs itself.

The API includes business create/list/get/update/archive; branch
create/list/get/update/archive/reactivate with optional city/country filters;
membership invite/accept/list/role/branch-access/revoke; and atomic ownership
transfer. Request bodies forbid undeclared fields. Only the trusted actor
dependency supplies the acting user's identity, and the application use cases
enforce tenant and membership authorization.

See [`examples/identity_business_consumer`](../examples/identity_business_consumer)
for the tested host composition of Identity OTP registration, Notification
queue, signed JWT/session validation, and Business routes. This sample has a
capturing notification queue for tests, **not a production delivery worker**.
The host must validate invited user IDs against its Identity user records and
decide how to send invitation notifications.

From this directory, install the locked development environment and run quality checks:

```bash
uv sync --extra test --locked
make check
```

The `check` target runs Ruff lint/format checks, strict Pyright, branch-aware pytest
coverage (minimum 85%), and wheel/sdist builds. A dedicated GitHub Actions workflow
also checks the distribution in a clean virtual environment.

A business with zero branches is a first-class use case. Creating a business does not
implicitly create a branch, and no virtual/default branch is used.
`BranchAddress` may contain only a city, and physical address information remains
optional even when a branch exists.

## Illustrative host flow

1. A user signs in through Identity's OTP flow; Notification delivers the OTP via the host's configured provider.
2. The host verifies the resulting access token and resolves a trusted user identity.
3. Business creates or loads organizations and memberships for that identity, enforcing permissions.
4. The user selects an authorized business and optionally a branch; the host passes trusted scope to its own business-specific modules.

The same identity may repeat this flow for another business without registering again.

## Implementation

The first implementation targets a lean, reusable core. See [ROADMAP.md](ROADMAP.md) for stage order, test gates, deliberate exclusions and release criteria. Business, branch, membership, SQL persistence and optional FastAPI APIs are implemented. The package has not yet been published as a distribution.

## Usage guide

### Installation

Use Python 3.12 or newer. Until the package is published, install it from the
`business` directory of this repository:

```bash
pip install ./business
pip install './business[sqlalchemy]'
pip install './business[fastapi,postgres]'
```

Choose **one** of these alternatives based on the required capabilities. The
base installation needs no FastAPI or SQLAlchemy. `sqlalchemy` adds the async
persistence adapter, `postgres` additionally installs `asyncpg`, and `fastapi`
adds the optional HTTP router. For development inside `business/`, use
`uv sync --extra test --locked` instead. The distribution name is
`hamresan-business`; the Python import name is `business`.

### Compose the application services

The host owns its database engine, connection pool, session lifecycle,
authentication and database migrations. A reusable composition function can
accept an existing SQLAlchemy session maker:

```python
from business.bootstrap import BusinessApplicationFactory
from business.infrastructure.clock import SystemClock
from business.infrastructure.identifiers import UuidIdentifierGenerator
from business.infrastructure.persistence.sqlalchemy import (
    BranchMapper,
    BusinessMapper,
    MembershipAuditMapper,
    MembershipMapper,
    SqlAlchemyBusinessUnitOfWorkFactory,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def build_business_services(
    session_maker: async_sessionmaker[AsyncSession],
) -> BusinessApplicationFactory:
    unit_of_work = SqlAlchemyBusinessUnitOfWorkFactory(
        session_maker,
        BusinessMapper(),
        BranchMapper(),
        MembershipMapper(),
        MembershipAuditMapper(),
    )
    return BusinessApplicationFactory(
        unit_of_work,
        SystemClock(),
        UuidIdentifierGenerator(),
    )
```

Create the `async_sessionmaker` in your application's composition root, for
example from an engine created with `create_async_engine(...)`. Configure
PostgreSQL with a `postgresql+asyncpg://...` URL. Do not create an engine in a
request handler, and do not call `metadata.create_all()` on a production
database; use host-owned Alembic revisions instead.

### Use the framework-independent Python API

All commands receive the **authenticated actor separately**. The actor ID
must originate from a trusted login/session boundary; it is not an arbitrary
value supplied by the customer. After building `services` above:

```python
from business import AuthenticatedActor, CreateBusinessCommand, CreateBranchCommand


async def create_organization(services, trusted_user_id):
    actor = AuthenticatedActor(user_id=trusted_user_id)
    business = await services.businesses().create.execute(
        CreateBusinessCommand(
            name="Muscat Clinic",
            country_code="OM",
            default_language="en",
            default_currency_code="OMR",
        ),
        actor=actor,
    )

    # A business may stay branchless; create a branch only when needed.
    branch = await services.branches().create.execute(
        CreateBranchCommand(
            business_id=business.id,
            name="Main Branch",
            timezone="Asia/Muscat",
        ),
        actor=actor,
    )
    return business, branch
```

The same actor may create multiple unrelated businesses. Each business starts
with that actor as its only active Owner. A branch can have an optional
`BranchAddress(city="Muscat", country_code="OM")` and `BranchContact`; it
does not require a street address. The `timezone` must be a valid IANA name.

Use the corresponding command objects for updates, invitations, role changes,
branch-access changes and ownership transfer. For example:

```python
from business.application import (
    InviteMemberCommand,
    SetMemberBranchAccessCommand,
    TransferOwnershipCommand,
)
from business import BranchAccessScope


async def manage_members(services, actor, business_id, invited_user_id, branch_id):
    invitation = await services.memberships().invite.execute(
        InviteMemberCommand(business_id=business_id, user_id=invited_user_id),
        actor=actor,
    )
    # The invitee must separately accept with their own authenticated actor.
    # An Owner can then grant access to a selected branch.
    await services.memberships().set_access.execute(
        SetMemberBranchAccessCommand(
            business_id=business_id,
            membership_id=invitation.id,
            scope=BranchAccessScope.SELECTED,
            branch_ids=(branch_id,),
        ),
        actor=actor,
    )
    # Ownership transfer requires a DIFFERENT, already active member.
    # It is never performed automatically when inviting someone.
```

For an ownership transfer, call
`services.memberships().transfer.execute(TransferOwnershipCommand(business_id,
recipient_membership_id), actor=current_owner)` only after the recipient has
accepted their invitation. The prior Owner becomes a Manager, and a database
constraint prevents two simultaneously active Owners. Ordinary role changes
cannot create or demote an Owner.

### Check business roles and branch access from other packages

`BusinessApplicationFactory.authorization()` returns a read-only service that
implements the public `BusinessAuthorizationReader` contract. Other packages
can depend on this contract instead of querying Business tables directly.
The host creates and injects the implementation using the same unit-of-work
configuration shown above:

```python
from business.application import BusinessAuthorizationReader
from business.domain import MembershipRole


async def can_manage_appointments(
    authorization: BusinessAuthorizationReader,
    business_id,
    branch_id,
    trusted_user_id,
) -> bool:
    is_manager = await authorization.has_role(
        business_id,
        trusted_user_id,
        frozenset({MembershipRole.OWNER, MembershipRole.MANAGER}),
    )
    return is_manager and await authorization.can_access_branch(
        business_id, branch_id, trusted_user_id
    )


# Host composition root:
# authorization: BusinessAuthorizationReader = services.authorization()
```

The three methods are:

| Query | Return | Meaning |
| --- | --- | --- |
| `get_membership(business_id, user_id)` | `MembershipAuthorizationInfo \| None` | Immutable summary with `business_id`, `user_id`, `role`, `status` and `branch_access_scope`; current active or invited membership only |
| `has_role(business_id, user_id, allowed_roles)` | `bool` | `True` only for an active membership matching one of the supplied roles |
| `can_access_branch(business_id, branch_id, user_id)` | `bool` | `True` only for an active member authorized for a branch of that same business |

`allowed_roles` is a `frozenset[MembershipRole]`; an empty set denies access.
Invited, revoked, missing and cross-business memberships never grant role or
branch access. Revoked historical memberships are not returned by
`get_membership` because its repository resolves only current memberships.
Owners/Managers have access to all branches, Members may have `ALL` or
`SELECTED` scope, and an empty selected scope denies access to every branch.
The service checks that the referenced branch exists in the given business.
As with the existing Business read API, archived businesses and branches
remain readable; this **does not** authorize mutations to archived resources.

These are organization-level facts, **not** a general action-permission
system. A consuming package must decide which role can perform each of its
own operations and enforce additional business rules. The host must derive
`trusted_user_id` and selected tenant scope from authenticated/authorized
context; neither value should be trusted merely because a client submitted
it. No JWT, Identity adapter or new database table is required.

### Add the FastAPI routes

The optional adapter mounts the REST routes onto an existing host application.
It does **not** authenticate users. The host must inject an async callable that
verifies credentials and returns a trusted `AuthenticatedActor` or raises an
HTTP authentication error:

```python
from business.presentation import build_fastapi_business_adapter
from fastapi import FastAPI


def install_business_api(app: FastAPI, services, authenticated_actor_dependency):
    adapter = build_fastapi_business_adapter(
        authenticated_actor_dependency=authenticated_actor_dependency,
        businesses=services.businesses(),
        branches=services.branches(),
        memberships=services.memberships(),
    )
    adapter.install(app)
```

For a **working authentication integration** (Identity OTP, Notification queue,
real signed JWT, token verification and conversion to an `AuthenticatedActor`),
see [the host example](../examples/identity_business_consumer/README.md) and
its executable integration test. Do not accept a `user_id` from HTTP request
headers or JSON as proof of authentication.

### HTTP endpoint reference

All endpoints require the host's authentication dependency. Path parameters
`business_id`, `branch_id` and `membership_id` are UUIDs. `POST /businesses`
and `POST /businesses/{business_id}/branches` return `201`; most other
successful operations return `200` with the updated resource.

| Method | Path | Required access | Purpose |
| --- | --- | --- | --- |
| `POST` | `/businesses` | Authenticated user | Create a business and become its Owner |
| `GET` | `/businesses` | Authenticated user | List businesses with active membership |
| `GET` | `/businesses/{business_id}` | Active member | Read a business |
| `PUT` | `/businesses/{business_id}` | Owner | Replace editable business profile |
| `DELETE` | `/businesses/{business_id}` | Owner | Archive without deleting history |
| `POST` | `/businesses/{business_id}/branches` | Owner or Manager | Create branch |
| `GET` | `/businesses/{business_id}/branches` | Active member | List visible branches; `city` and `country_code` filters |
| `GET` | `/businesses/{business_id}/branches/{branch_id}` | Authorized branch member | Read a branch |
| `PUT` | `/businesses/{business_id}/branches/{branch_id}` | Owner or Manager | Replace branch details |
| `DELETE` | `/businesses/{business_id}/branches/{branch_id}` | Owner or Manager | Archive branch |
| `POST` | `/businesses/{business_id}/branches/{branch_id}/reactivate` | Owner or Manager | Reactivate branch |
| `POST` | `/businesses/{business_id}/memberships` | Owner | Invite an existing external user ID |
| `POST` | `/businesses/{business_id}/memberships/accept` | Invited user | Accept one's own invitation |
| `GET` | `/businesses/{business_id}/memberships` | Owner | List memberships |
| `PUT` | `/businesses/{business_id}/memberships/{membership_id}/role` | Owner | Switch Manager/Member role |
| `PUT` | `/businesses/{business_id}/memberships/{membership_id}/access` | Owner | Set selected/all branch access |
| `DELETE` | `/businesses/{business_id}/memberships/{membership_id}` | Owner | Revoke membership |
| `POST` | `/businesses/{business_id}/ownership/transfer` | Current Owner | Transfer to another active member |

Request bodies use strict Pydantic schemas (`extra="forbid"`). Example JSON:

```json
{
  "name": "Muscat Clinic",
  "country_code": "OM",
  "default_language": "en",
  "default_currency_code": "OMR",
  "business_type": "clinic"
}
```

Branch creation accepts `name`, `timezone`, optional `address` and optional
`contact`. An address may contain `country_code`, `state_or_province`, `city`,
`area`, `street`, `building`, `postal_code`, and `additional_details`; contact
may contain `phone` and `email`. The branch-list filters are case-insensitive.

Membership request bodies:

| Operation | Example JSON |
| --- | --- |
| Invite | `{"user_id": "<user-uuid>"}` |
| Change role | `{"role": "manager"}` or `{"role": "member"}` |
| Restrict branches | `{"scope": "selected", "branch_ids": ["<branch-uuid>"]}` |
| Unrestricted access | `{"scope": "all", "branch_ids": []}` |
| Transfer ownership | `{"recipient_membership_id": "<membership-uuid>"}` |

Invitations initially grant **no branch access**. They only become active
after the invited identity accepts them. Owners and Managers can access all
branches; a Member with selected scope sees only explicitly granted branches.
An empty selected list means no branches. `all` must not include branch IDs.

HTTP errors include `401` from the host authentication dependency, `403` for
insufficient permissions, `404` for missing or hidden resources, `409` for
invalid state transitions or conflicts, and `422` for invalid input. Archive
operations preserve IDs and historical references rather than deleting rows.

### Alembic migrations and production responsibilities

Import `business.migrations.business_metadata()` into the host's Alembic
configuration. Compose it with other packages' metadata (for example
`identity.migrations.identity_metadata()`) through the host's migration
process. `include_business_name(...)` can filter table/index reflection to
Business-owned tables. The package owns five `business_` tables and their
constraints, but **does not ship a host-specific migration history**.

The host must:

1. Maintain and apply versioned Alembic revisions before serving requests.
2. Configure its async session factory and use a separate PostgreSQL test database.
3. Authenticate Identity users, validate invite targets and authorize host-level operations.
4. Store credentials securely, avoid logging sensitive contact or authentication data, and configure per-tenant access policies where needed.
5. Run its Notification queue/worker if it wants to deliver invitations or OTPs.

### Run the quality and integration tests

From `business/`:

```bash
uv sync --extra test --locked
make check
```

The PostgreSQL concurrency test is skipped unless
`BUSINESS_TEST_POSTGRES_DSN` names a dedicated test database:

```bash
export BUSINESS_TEST_POSTGRES_DSN='postgresql+asyncpg://business_test:password@127.0.0.1:5433/business_test'
uv run pytest tests/infrastructure/test_postgresql_concurrency.py -v
```

For the cross-package Identity/Notification/Business integration tests:

```bash
cd ../examples/identity_business_consumer
uv sync --extra test --locked
uv run pytest -v
```

Ruff, strict Pyright, coverage and wheel/sdist construction are part of
`make check`. CI additionally verifies clean installation of the built wheel
with and without optional FastAPI/SQLAlchemy dependencies.
