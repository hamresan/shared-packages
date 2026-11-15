# hamresan-business

Reusable business, branch, and organization-membership management for Python applications.

> **Status: Stage 2 business application core implemented.** The source is locally installable, but no distribution has been published. Branch management, general membership operations, SQLAlchemy persistence, and HTTP integration remain planned for later stages in [ROADMAP.md](ROADMAP.md).

## Purpose

`hamresan-business` provides a reusable foundation for applications that manage one or many businesses, each with zero, one, or multiple branches. An individual can own or participate in multiple businesses without a one-business-per-user restriction.

The package manages business organization and access relationships; it does not implement authentication, staff scheduling, payroll, commerce, or other application-specific operations.

## Supported organization models

| Scenario | Expected behavior |
| --- | --- |
| Single-location business | One `Business` with one `Branch`; no special single-branch model needed. |
| Multi-branch business | One `Business` with multiple independently identified branches. |
| Multiple businesses per individual | One identity can own or belong to multiple distinct businesses. |
| Multiple users per business | Several identities can have memberships with different roles. |
| Non-physical organization | A `Business` can exist before a branch is created; zero branches is valid during setup. |

The business-to-branch relationship is one-to-many. The user-to-business relationship is many-to-many through memberships. Ownership is **a membership role**, not an exclusive `owner_user_id` column or a unique constraint on `user_id`.

## Planned core models

### Business

The organizational and tenant root. Initially includes a stable UUID, name, optional business type/category, country, default language/currency, lifecycle status, and timestamps. A business is not automatically a physical location.

### Branch

Belongs to exactly one business and has its own UUID, name, optional address/contact details, IANA timezone, active/archived status, and timestamps. Branch settings override business defaults only where explicitly supported. Historical branch references must remain stable when a branch is archived.

### BusinessMembership

Links an external identity `user_id` to a business, with a role and membership status. The same identity may have multiple memberships, including ownership in several businesses. An active business must not accidentally lose its final active owner.

### Branch access (narrow extension)

Some applications need to restrict a member to selected branches. This will be supported by an optional membership-to-branch access association, with explicit business-scope validation. Branch scoping complements, rather than replaces, business-level authorization. Avoid implementing a generic policy language or universal RBAC engine.

## Employee management boundary

The package distinguishes **organization membership** from **employment**:

- **In scope:** authenticated users' memberships, owner/member roles, invitation and membership status, and optional access to specific branches.
- **Out of scope:** employee records without user accounts, contracts, payroll, attendance, leave, professional qualifications, shift planning, resource capacity, and operational assignments.

An employee may not have a login, and a business member may not be an employee. Keeping these concepts separate prevents unrelated applications from inheriting a workforce-management system. Applications can build their own staff domain or use a dedicated workforce package when there is proven shared demand.

## Authentication and notifications

`hamresan-business` **does not issue OTPs, authenticate passwords/tokens, or send messages itself**.

- [`hamresan-identity`](../identity) handles registration/login using email or mobile OTP, sessions, access tokens, revocation, and authenticated principals.
- [`hamresan-notification`](../notification) provides notification contracts and delivery infrastructure; Identity uses its `NotificationSender` for OTP delivery.
- The **host application** composes Identity and Notification, authenticates each request, and converts the trusted principal into a small Business-owned `AuthenticatedActor` contract.
- Business use cases enforce membership and resource authorization. Raw `user_id`, role, or ownership supplied by a request body is never authoritative.
- Future invitation notifications may be dispatched through an injected notification contract or a host-owned integration; this package must not create its own notification worker or OTP flow.

The domain/application core must remain independent of concrete Identity and Notification implementations. An optional integration example will demonstrate their composition with this package, including a real JWT/session implementation rather than an example-only token stub.

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

## Implemented application core (Stages 1–2)

The package exposes framework-independent primitives and use cases:

- `AuthenticatedActor` is a trusted, host-resolved user identity; commands never accept
  an owner ID or role as proof of authorization.
- `CreateBusinessService` creates a business and its active owner membership within
  one injected unit of work. The persistence adapter must commit both atomically.
- `GetBusinessService` and `ListBusinessesService` return only businesses visible to
  the actor through active membership.
- `UpdateBusinessService` and `ArchiveBusinessService` require an active owner role.
  An archived business can still be read, but cannot be edited or archived twice.
- `BranchAddress` includes optional `city` and `country_code`. Branch CRUD and
  branch-scoped permissions are not part of Stage 2.

The public business profile update is a **full profile replacement** (`name` and
`business_type`); passing `business_type=None` explicitly clears it. Country,
language, and currency settings are retained by profile updates.

The application services require injected `BusinessUnitOfWorkFactory`, factories,
validators, policies, and clocks. Stage 2 tests exercise those use cases against an
explicit in-memory implementation of the repository/unit-of-work contracts.
Database-backed transaction guarantees will be implemented and PostgreSQL-tested
in Stage 5; no SQLAlchemy adapter or HTTP route is claimed to exist yet.

From this directory, install the locked development environment and run quality checks:

```bash
uv sync --extra test --locked
make check
```

The `check` target runs Ruff lint/format checks, strict Pyright, branch-aware pytest
coverage (minimum 85%), and wheel/sdist builds. A dedicated GitHub Actions workflow
also checks the distribution in a clean virtual environment.

A business with zero branches is a first-class use case. Creating a business does not
implicitly create a branch; Stage 3 will introduce independent branch management.
`BranchAddress` may contain only a city, and physical address information will remain
optional even when a branch exists.

## Illustrative host flow

1. A user signs in through Identity's OTP flow; Notification delivers the OTP via the host's configured provider.
2. The host verifies the resulting access token and resolves a trusted user identity.
3. Business creates or loads organizations and memberships for that identity, enforcing permissions.
4. The user selects an authorized business and optionally a branch; the host passes trusted scope to its own business-specific modules.

The same identity may repeat this flow for another business without registering again.

## Implementation

The first implementation targets a lean, reusable core. See [ROADMAP.md](ROADMAP.md) for stage order, test gates, deliberate exclusions and release criteria. Business creation and management use cases are available through the Python application API; HTTP endpoints, persistence adapters, and distribution publication are not yet available.
